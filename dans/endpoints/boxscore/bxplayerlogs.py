'''Player Logs Endpoint'''
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

from dans.endpoints._base import LogsEndpoint
from dans.library.parameters import SeasonType
from dans.library.request.request import Request

class BXPlayerLogs(LogsEndpoint):
    '''Finds a player's game logs within a given range of years'''

    expected_columns = [
        'SEASON',
        'SEASON_TYPE',
        'GAME_DATE',
        'PLAYER_NAME',
        'TEAM',
        'LOCATION',
        'MATCHUP',
        'WL',
        'MIN',
        'FGM',
        'FGA',
        'FG_PCT',
        'FG3M',
        'FG3A',
        'FG3_PCT',
        'FTM',
        'FTA',
        'FT_PCT',
        'OREB',
        'DREB',
        'REB',
        'AST',
        'STL',
        'BLK',
        'TOV',
        'PF',
        'PTS',
        'PLUS_MINUS'
    ]
    
    error = None

    def __init__(
        self,
        name,
        year_range,
        season_type=SeasonType.default
    ):
        self.name = name
        self.year_range = year_range
        self.season_type = season_type
        self.suffix = self._lookup(name)

    def _lookup(self, name):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            'data/player_names.csv')
        names_df = pd.read_csv(path)

        player = names_df[names_df["NAME"] == name]["SUFFIX"]
        if len(player) == 0:
            self.error = f"Player not found: `{name}`"
            return None
        return player.iloc[0]

    def bball_ref(self):
        '''Uses bball-ref to find player game logs.'''

        if self.year_range[0] < 1971:
            self.error = "This API does not have support for bball-ref before 1970-71."
            return pd.DataFrame()

        if not self.suffix:
            return pd.DataFrame()

        format_suffix = 'players/' + self.suffix[0] + '/' + self.suffix
        iterator = tqdm(range(self.year_range[0], self.year_range[1] + 1),
                        desc="Loading player game logs...", ncols=75, leave=False)

        dfs = []
        for curr_year in iterator:
            if self.season_type == SeasonType.playoffs:
                url = f'https://www.basketball-reference.com/{format_suffix}/gamelog-playoffs/'
                attr_id = "player_game_log_post"
            else:
                url = f'https://www.basketball-reference.com/{format_suffix}/gamelog/{curr_year}'
                attr_id = "player_game_log_reg"

            data_pd = Request(url=url, attr_id={"id": attr_id}).get_response()
            if data_pd.empty:
                return pd.DataFrame()

            if len(data_pd.columns) < 10:
                continue

            data_pd = data_pd.drop(columns=["Gtm", "GS"], axis=1)\
                .replace("", np.nan)

            data_pd = data_pd[~(
                (data_pd["Gcar"].astype(str).str.contains("nan")) |
                (data_pd["Gcar"].astype(str).str.contains("none"))
                )]\
                .rename(columns={
                    data_pd.columns[1]: "GAME_DATE",
                    'Result': 'WL',
                    "Team": "TEAM",
                    "Opp": "MATCHUP",
                    "MP": "MIN",
                    "": "LOCATION",
                    "FG": "FGM",
                    "FG%": "FG_PCT",
                    "3P": "FG3M",
                    "3PA": "FG3A",
                    "3P%": "FG3_PCT",
                    "FT": "FTM",
                    "FT%": "FT_PCT",
                    "ORB": "OREB",
                    "DRB": "DREB",
                    "TRB": "REB",
                    "+/-": "PLUS_MINUS"
                })\
                .dropna(subset=["AST"])\
                .drop(columns=["Gcar"])

            # Calculate Season from Game Date column instead of using `curr_year` because playoff
            # game logs shows for all years
            if self.season_type == SeasonType.regular_season:
                data_pd["SEASON"] = curr_year
            else:
                data_pd["SEASON"] = data_pd["GAME_DATE"].str[0:4].astype(int)
            data_pd["MIN"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):').astype("int32") + \
                            data_pd["MIN"].str.extract(r':([0-5][0-9])').astype("int32") / 60

            convert_dict = {
                'SEASON': 'int32', 'GAME_DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string',
                'MIN': 'float64','FGM': 'int32', 'FGA': 'int32', 'FG_PCT': 'float64', 'FG3M': 'float32',
                'FG3A': 'float32', 'FG3_PCT': 'float64', 'FTM': 'int32', 'FTA': 'int32',
                'FT_PCT': 'float32', 'OREB': 'float32', 'DREB': 'float32', 'REB': 'int32',
                'AST' : 'int32', 'STL': 'float32', 'BLK': 'float32', 'TOV' : 'float32',
                'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64', 'PLUS_MINUS' : 'float32',
                '2P': 'float32', "2PA": 'float32', '2P%': 'float64', 'eFG%': "float64",
                'LOCATION': 'string', 'WL': 'string'
            }
            data_pd = data_pd.astype({key: convert_dict[key] for key in data_pd.columns.values})

            dfs.append(data_pd)

            if self.season_type == SeasonType.playoffs:
                for _ in iterator:
                    pass
                break
            continue

        result = pd.concat(dfs)\
            .query("SEASON >= @self.year_range[0] and SEASON <= @self.year_range[1]")
        result["PLAYER_NAME"] = self.name
        result["LOCATION"] = result['LOCATION'].replace(np.nan, "vs")
        result["SEASON_TYPE"] = self.season_type
        result['WL'] = result['WL'].str[0]
        # Some stats were not tracked in the 1970s, so we add those columns with value np.nan
        result.loc[:, list(set(self.expected_columns) - set(result.columns.values))] = np.nan

        if self.error:
            print(self.error)
        return result[self.expected_columns].reset_index(drop=True)

    def nba_stats(self):
        '''Uses nba-stats to find player game logs'''

        if self.year_range[0] < 1997:
            self.error = "This API does not have support for nba-stats before 1996-97."
            return pd.DataFrame()

        if not self.suffix:
            return pd.DataFrame()

        iterator = tqdm(range(self.year_range[0], self.year_range[1] + 1),
                        desc="Loading player game logs...", ncols=75, leave=False)

        dfs = []
        for curr_year in iterator:
            url = 'https://stats.nba.com/stats/playergamelogs'
            year_df = Request(
                url=url,
                year=curr_year,
                season_type=self.season_type,
                per_mode="PerGame"
            ).get_response()
            
            if year_df.empty:
                return pd.DataFrame()

            year_df = year_df.query('PLAYER_NAME == @self.name')\
                [['SEASON_YEAR', 'GAME_DATE', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'MATCHUP', 'WL',
                'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT',
                'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'PTS', 'PLUS_MINUS']]\
                .rename(columns={
                    'SEASON_YEAR': 'SEASON', 'TEAM_ABBREVIATION': 'TEAM'})[::-1]
            year_df['GAME_DATE'] = year_df['GAME_DATE'].str[:10]
            year_df['LOCATION'] = ''
            year_df.loc[(year_df['MATCHUP'].str.contains('@')), 'LOCATION'] = '@'
            year_df['MATCHUP'] = year_df['MATCHUP'].str[-3:]
            year_df['SEASON'] = curr_year

            dfs.append(year_df)

        if len(dfs) == 0:
            return pd.DataFrame()

        result = pd.concat(dfs)\
            .astype({
                'FGM': 'int32', 'FGA': 'int32', 'FG3M': 'int32', 'FG3A': 'int32', 'FTA': 'int32',
                'FTM': 'int32', 'OREB': 'int32', 'DREB': 'int32', 'REB': 'int32', 'AST': 'int32',
                'TOV': 'int32', 'STL': 'int32', 'BLK': 'int32', 'PF': 'int32', 'PTS': 'int32',
                'PLUS_MINUS': 'float32', 'SEASON': 'object'})

        result["SEASON_TYPE"] = self.season_type
        if self.error:
            print(self.error)
        return result[self.expected_columns].reset_index(drop=True)
