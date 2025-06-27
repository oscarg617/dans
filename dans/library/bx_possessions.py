"""Box score possession counter"""
from abc import ABC, abstractmethod
import pandas as pd
from tqdm import tqdm

from dans.library.parameters import SeasonType
from dans.library.request.request import Request

class PossCount(ABC):
    
    @abstractmethod
    def count(self, logs: pd.DataFrame):
        pass

class BBallRefPossCount(PossCount):
    
    def count(self, logs: pd.DataFrame):
        
        pace_list = pd.DataFrame(logs.groupby(['SEASON', 'SEASON_TYPE', 'TEAM'])
                                 .size().reset_index())

        iterator = tqdm(range(len(pace_list)),
                        desc='Loading player possessions...', ncols=75, leave=False)

        poss_list = []
        for i in iterator:
            year = pace_list.loc[i]["SEASON"]
            team = pace_list.loc[i]["TEAM"]
            season_type = pace_list.loc[i]["SEASON_TYPE"]
            url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog-advanced/'

            if season_type == SeasonType.regular_season:
                attr_id = "team_game_log_adv_reg"
            else:
                attr_id = "team_game_log_adv_post"

            adv_log_pd = Request(url=url, attr_id={"id": attr_id}).get_response()
            if adv_log_pd.empty:
                return None

            if 'Pace' not in adv_log_pd.columns:
                for _ in iterator:
                    pass

                self.error = "Failed to estimate player possessions. Pace was not tracked " + \
                         f"during the {year} {season_type}"
                return None

            adv_log_pd = adv_log_pd\
                .iloc[:, [i for i in range(len(adv_log_pd.columns)) if i != 6]]\
                .rename(columns={
                    "Date": "GAME_DATE",
                    "Opp": "MATCHUP"
                })

            poss_df = pd.merge(logs, adv_log_pd, on=["GAME_DATE", "MATCHUP"], how="inner")

            if (poss_df["Pace"] == "").any():

                for _ in iterator:
                    pass

                self.error = 'Failed to estimate player possessions. At least one of the ' + \
                         'games does not track pace.'
                return None

            poss_df["POSS"] = ( poss_df["MIN"].astype(float) / 48 ) * \
                poss_df["Pace"].astype(float)
            
            poss_list.append(poss_df)

        return pd.concat(poss_list)

class NBAStatsPossCount(PossCount):

    def count(self, logs: pd.DataFrame):

        pace_list = pd.DataFrame(logs.groupby(['SEASON', 'SEASON_TYPE'])
                                 .size().reset_index())

        iterator = tqdm(range(len(pace_list)),
                        desc='Loading player possessions...', ncols=75, leave=False)

        poss_list = []
        for i in iterator:
            year = pace_list.loc[i]["SEASON"]
            season_type = pace_list.loc[i]["SEASON_TYPE"]
            url = 'https://stats.nba.com/stats/playergamelogs'
            adv_log_pd = Request(
                url=url,
                year=year,
                season_type=season_type,
                measure_type="Advanced"
            ).get_response()
            if adv_log_pd.empty:
                return None

            adv_log_pd = adv_log_pd.query('PLAYER_NAME == @logs.iloc[0]["PLAYER_NAME"]')\
                .iloc[:, [i for i in range(len(adv_log_pd.columns)) if i != 11]]
            
            adv_log_pd["GAME_DATE"] = adv_log_pd["GAME_DATE"].str[:10]

            poss_df = pd.merge(logs, adv_log_pd, on=["GAME_DATE"], how="inner")
            poss_list.append(poss_df)

        return pd.concat(poss_list)
