'''Player Stats Endpoint.'''
import sys
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

from dans.library.arguments import SeasonType, DataFormat
from dans.library.request import Request
from dans.library import constants
from dans.endpoints._base import Endpoint
from dans.endpoints.playerlogs import PlayerLogs
from dans.endpoints.teams import Teams

class PlayerStats(Endpoint):
    '''Calculates players stats against opponents within a given range of defensive strength'''

    expected_columns = [
        "PTS",
        "TRB",
        "AST",
        "TS%",
        "rTS%",
        "DRTG"
    ]

    def __init__(
        self,
        _name,
        year_range: list,
        drtg_range: list,
        data_format=DataFormat.default,
        season_type=SeasonType.default
    ):
        self.name = _name
        self.year_range = year_range
        self.drtg_range = drtg_range
        self.data_format = data_format
        self.season_type = season_type

    def bball_ref(self):
        '''Uses bball-ref to calculate player logs and team defensive metrics.'''
        logs_df = PlayerLogs(self.name, self.year_range, self.season_type).bball_ref()
        teams_df = Teams(self.year_range, self.drtg_range).bball_ref()
        add_possessions = self._bball_ref_add_possessions
        return self._calculate_stats(logs_df, teams_df, add_possessions)

    def nba_stats(self):
        '''Uses nba-stats to calculate player logs and team defensive metrics.'''
        logs_df = PlayerLogs(self.name, self.year_range, self.season_type).nba_stats()
        teams_df = Teams(self.year_range, self.drtg_range).nba_stats()
        add_possessions = self._nba_stats_add_possessions
        return self._calculate_stats(logs_df, teams_df, add_possessions)

    def _calculate_stats(
            self,
            logs_df: pd.DataFrame,
            teams_df: pd.DataFrame,
            add_possessions
    ):

        if len(logs_df) == 0 or len(teams_df) == 0:
            print("No logs found.")
            sys.exit(1)

        teams_df = self._filter_teams_through_logs(logs_df, teams_df)
        teams_dict = self._teams_df_to_dict(teams_df)
        logs_df = self._filter_logs_through_teams(logs_df, teams_dict)

        opp_drtg, player_true_shooting, relative_true_shooting = \
            self._calculate_efficiency_stats(logs_df, teams_df, teams_dict)

        if self.data_format == DataFormat.per_game:
            points, rebounds, assists = self._per_game_stats(logs_df)
        elif self.data_format == DataFormat.per_100_poss:
            points, rebounds, assists = self._per_100_poss_stats(
                logs_df, teams_dict, add_possessions)
        elif self.data_format == DataFormat.pace_adj:
            points, rebounds, assists = self._pace_adj_stats(
                logs_df, teams_dict, add_possessions)
        elif self.data_format == DataFormat.opp_adj:
            points, rebounds, assists = self._opp_adj_stats(logs_df, opp_drtg)
        elif self.data_format == DataFormat.opp_pace_adj:
            points, rebounds, assists = self._opp_pace_adj_stats(
                logs_df, teams_dict, add_possessions, opp_drtg)
        else:
            print(f"Not a valid data format: {self.data_format}")
            sys.exit(1)

        return pd.DataFrame(columns=self.expected_columns, data=[[
            points,
            rebounds,
            assists,
            player_true_shooting,
            relative_true_shooting,
            opp_drtg
        ]])

    def _per_game_stats(
            self,
            logs_df: pd.DataFrame
    ):
        points = round(logs_df['PTS'].mean(), 1)
        rebounds = round(logs_df['TRB'].mean(), 1)
        assists = round(logs_df['AST'].mean(), 1)
        return (points, rebounds, assists)

    def _per_100_poss_stats(
            self,
            logs_df: pd.DataFrame,
            teams_dict: dict,
            add_possessions
    ):
        possessions = add_possessions(self.name, logs_df, teams_dict, self.season_type)
        points = round((logs_df['PTS'].sum() / possessions) * 100, 1)
        rebounds = round((logs_df['TRB'].sum() / possessions) * 100, 1)
        assists = round((logs_df['AST'].sum() / possessions) * 100, 1)
        return (points, rebounds, assists)

    def _pace_adj_stats(
            self,
            logs_df: pd.DataFrame,
            teams_dict: dict,
            add_possessions
    ):
        possessions = add_possessions(self.name, logs_df, \
                                            teams_dict, self.season_type)
        min_ratio = logs_df['MIN'].mean() / 48
        points = round((min_ratio * (logs_df['PTS'].sum() / possessions) * 100), 1)
        rebounds = round((min_ratio * (logs_df['TRB'].sum() / possessions) * 100), 1)
        assists = round((min_ratio * (logs_df['AST'].sum() / possessions) * 100), 1)
        return points, rebounds, assists

    def _opp_adj_stats(
            self,
            logs_df: pd.DataFrame,
            opp_drtg: float
    ):
        points = round((logs_df['PTS'].mean() * (110 / opp_drtg)), 1)
        rebounds = round(logs_df['TRB'].mean(), 1)
        assists = round(logs_df['AST'].mean(), 1)
        return points, rebounds, assists

    def _opp_pace_adj_stats(
            self,
            logs_df: pd.DataFrame,
            teams_dict: dict,
            add_possessions,
            opp_drtg: int
    ):
        possessions = add_possessions(self.name, logs_df, \
                                            teams_dict, self.season_type)
        points_per_100 = (logs_df['PTS'].sum() / possessions) * 100
        points = round(((logs_df['MIN'].mean() / 48) * points_per_100 * (110 / opp_drtg)), 1)
        rebounds = round(logs_df['TRB'].mean(), 1)
        assists = round(logs_df['AST'].mean(), 1)
        return points, rebounds, assists

    def _filter_teams_through_logs(
            self,
            logs_df: pd.DataFrame,
            teams_df: pd.DataFrame
    ):
        dfs = []
        for log in range(logs_df.shape[0]):
            df_team = teams_df[teams_df['TEAM'] == logs_df.iloc[log].MATCHUP]
            df_year = df_team[df_team['SEASON'] == logs_df.iloc[log].SEASON]
            dfs.append(df_year)
        all_dfs = pd.concat(dfs)
        result = all_dfs.drop_duplicates()
        return result

    def _teams_df_to_dict(
            self,
            teams_df: pd.DataFrame
    ):
        if not teams_df.empty:
            df_list = list(zip(teams_df.SEASON, teams_df.TEAM))
            rslt = {}
            length = len(df_list)
            for index in range(length):
                if df_list[index][0] in rslt:
                    rslt[df_list[index][0]].append(df_list[index][1])
                else:
                    rslt[df_list[index][0]] = [df_list[index][1]]
            return rslt
        return None

    def _filter_logs_through_teams(
            self,
            logs_df: pd.DataFrame,
            teams_dict: dict
    ):
        dfs = []
        for year in teams_dict:
            length_value = len(teams_dict[year])
            for team_index in range(length_value):
                abbr = teams_dict[year][team_index]
                df_team = logs_df[logs_df['MATCHUP'] == abbr]
                df_year = df_team[df_team['SEASON'] == year]
                dfs.append(df_year)
        result = pd.concat(dfs)
        return result

    def _true_shooting_percentage(self, pts, fga, fta):
        return pts / (2 * (fga + (0.44 * fta)))

    def _calculate_efficiency_stats(
        self,
        logs_df: pd.DataFrame,
        teams_df: pd.DataFrame,
        teams_dict: dict
    ):
        opp_drtg_sum = 0
        opp_true_shooting_sum = 0
        for year in teams_dict:
            for opp_team in teams_dict[year]:
                logs_in_year = logs_df[logs_df['SEASON'] == year]
                logs_vs_team = logs_in_year[logs_in_year['MATCHUP'] == opp_team]
                opp_drtg_sum += (float(teams_df[teams_df['TEAM'] == opp_team].DRTG.values[0]) *
                                logs_vs_team.shape[0])
                teams_in_year = teams_df[teams_df['SEASON'] == year]
                opp_true_shooting_sum += (float(teams_in_year[teams_in_year['TEAM'] == opp_team]
                                                .OPP_TS.values[0]) * logs_vs_team.shape[0])
        opp_drtg = round((opp_drtg_sum / logs_df.shape[0]), 1)
        opp_true_shooting = (opp_true_shooting_sum / logs_df.shape[0]) * 100
        player_true_shooting = self._true_shooting_percentage(
            logs_df.PTS.sum(), logs_df.FGA.sum(), logs_df.FTA.sum()) * 100
        relative_true_shooting = round(player_true_shooting - opp_true_shooting, 1)
        return (opp_drtg, player_true_shooting, relative_true_shooting)

    def _bball_ref_add_possessions(
        self,
        _name,
        logs_df: pd.DataFrame,
        _team_dict: dict,
        _season_type
    ):
        total_poss = 0
        pace_list = pd.DataFrame(logs_df.groupby(['SEASON', 'TEAM']).size().reset_index())
        iterator = tqdm(range(len(pace_list)), desc='Loading player possessions...', ncols=75)
        
        for i in iterator:
            year = pace_list.loc[i]["SEASON"]
            team = pace_list.loc[i]["TEAM"]
            url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog-advanced/'

            if self.season_type == SeasonType.regular_season:
                attr_id = "team_game_log_adv_reg"
            else:
                attr_id = "team_game_log_adv_post"

            adv_log_pd = Request(url=url, attr_id={"id": attr_id}).get_response()
            if 'Pace' not in adv_log_pd.columns:

                for _ in iterator:
                    pass

                print("Failed to estimate player possessions. Pace was not tracked " + \
                         f"during the {year} {self.season_type}")
                sys.exit(1)

            adv_log_pd = adv_log_pd\
                .iloc[:, [i for i in range(len(adv_log_pd.columns)) if i != 6]]\
                .rename(columns={
                    "Date": "DATE",
                    "Opp": "MATCHUP"
                })
            
            poss_df = pd.merge(logs_df, adv_log_pd, on=["DATE", "MATCHUP"], how="inner")

            if (poss_df["Pace"] == "").any():

                for _ in iterator:
                    pass

                print('Failed to estimate player possessions. At least one of the ' + \
                         'games does not track pace.')
                sys.exit(1)
                
            poss_df["POSS"] = ( poss_df["MIN"].astype(float) / 48 ) * \
                poss_df["Pace"].astype(float)
            total_poss += poss_df["POSS"].sum()

        return total_poss

    # Credit to https://github.com/vishaalagartha for the following function

    def _get_game_suffix(self, date, team1, team2):
        url = "https://www.basketball-reference.com/boxscores/index.fcgi?year=" + \
                f"{date.year}&month={date.month}&day={date.day}"
        response = Request(function=requests.get, url=url).get_wrapper()
        if response.status_code != 200:
            return None

        suffix = None
        soup = BeautifulSoup(response.content, 'html.parser')
        for table in soup.find_all('table', attrs={'class': 'teams'}):
            for anchor in table.find_all('a'):
                if 'boxscores' in anchor.attrs['href'] and \
                    (team1 in anchor.attrs['href'] or team2 in anchor.attrs['href']):
                    suffix = anchor.attrs['href']
        return suffix

    def _nba_stats_add_possessions(
        self,
        _name,
        logs_df: pd.DataFrame,
        team_dict: dict,
        season_type
    ):

        total_poss = 0
        iterator = tqdm([self.year_range[0], self.year_range[1] + 1],
                        desc="Loading player possessions...", ncols=75)

        for year in iterator:
            url = 'https://stats.nba.com/stats/playergamelogs'
            adv_log_pd = Request(
                url=url,
                year=self._format_year(year),
                season_type=season_type,
                measure_type="Advanced"
            ).get_response()

            if adv_log_pd.empty:
                break

            adv_log_pd = adv_log_pd.query('PLAYER_NAME == @_name')\
                .iloc[:, [i for i in range(len(adv_log_pd.columns)) if i != 11]]\
                .rename(columns={"GAME_DATE": "DATE"})

            adv_log_pd["DATE"] = adv_log_pd["DATE"].str[:10]
            poss_df = pd.merge(logs_df, adv_log_pd, on=["DATE"], how="inner")
            total_poss += poss_df["POSS"].sum()

        return total_poss
