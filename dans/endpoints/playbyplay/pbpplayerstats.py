'''Player Stats Endpoint'''
import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm

from dans.endpoints._base import Endpoint
from dans.library.request import Request

from nba_api.stats.endpoints.gamerotation import GameRotation
from nba_api.stats.endpoints.playbyplayv2 import PlayByPlayV2
from nba_api.stats.endpoints.playbyplayv3 import PlayByPlayV3

pd.set_option('display.max_rows', None)

class PBPPlayerStats(Endpoint):
    
    def __init__(
        self,
        player_logs: pd.DataFrame,
        drtg_range: list
    ):
        self.player_logs = player_logs
        self.drtg_range = drtg_range
        self.stats = {}
        
        self.teams = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), "data\\nba-stats-teams.csv"))
        self.seasons = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), "data\\season-averages.csv"))
        
        print(player_logs)
        ids = player_logs["Player_ID"].unique().tolist()
        if len(ids) > 1:
            print(f"Error: There are {len(ids)} players included in the logs. There should " + 
                  "only be 1.")

        self.player_id = ids[0] if len(ids) == 1 else None
        
        self._iterate_through_games()
    
    def _iterate_through_games(self):
    
        iterator = self.player_logs.iterrows()
        pbp_logs = []
        for _, player_log in tqdm(iterator, desc='Loading game play-by-plays...', ncols=75):
            stats = self._player_game_stats(player_log['Game_ID'], player_log['SEASON'])
            pbp_logs.append(stats)
        
        self.data_frame = pd.DataFrame(pbp_logs)

    def _player_game_stats(
        self,
        game_id: str,
        season: str
    ) -> dict:

        # Two play-by-play logs are required. The V3 provides details relevant for scoring
        # stats, whereas V2 is more in depth with non-scoring plays.
        dflogs = pd.concat(Request(function=PlayByPlayV3, args={
            "game_id": game_id
        }).function_call().get_data_frames())
        dflogs2 = pd.concat(Request(function=PlayByPlayV2, args={
            "game_id": game_id
        }).function_call().get_data_frames())

        for score_team in ['scoreHome', 'scoreAway']:
            dflogs[score_team] = dflogs[score_team]\
                .replace(r'^\s*$', "0", regex=True)\
                .replace("0", np.nan)\
                .ffill()\
                .replace(np.nan, "0")\
                .astype(int)

        dflogs['margin'] = abs(dflogs['scoreAway'] - dflogs['scoreHome'])
        dflogs2['margin'] = dflogs2['SCOREMARGIN']\
            .replace("0", np.nan)\
            .ffill()\
            .replace(np.nan, "0")\
            .replace("TIE", "0")\
            .astype(int)

        dflogs = self._calculate_time(dflogs, 'clock')
        dflogs2 = self._calculate_time(dflogs2, 'PCTIMESTRING')

        # This is used to determine if a rebound is an offensive rebound.
        # This happens before any rows are eliminated so that we always know
        # what events actually happened right before a rebound occurs.
        dflogs['prevTeam'] = dflogs['teamId'].shift(1)
        dflogs['prevFGA'] = dflogs['isFieldGoal'].shift(1)
        dflogs['prevFTA'] = dflogs['actionType'].shift(1)

        dflogs, dflogs2, team_id, opp_tricode, bins = \
            self._handle_rotations(dflogs, dflogs2, game_id, self.player_id)

        all_logs, dflogs, dflogs2 = self._remove_garbage_time(dflogs, dflogs2, bins)
        
        stats = {
            "PLAYER_ID": self.player_id,
            "SEASON": season,
            "GAME_ID": game_id
        }
        stats["PTS"] = dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['shotResult'] == 'Made')]\
            ['shotValue'].sum() + len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['actionType'] == 'Free Throw') &
            (dflogs['description'].str.contains('PTS'))])
        stats["FTM"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['actionType'] == 'Free Throw') &
            (dflogs['description'].str.contains('PTS'))])
        stats["FGM"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['isFieldGoal'] == 1.0) &
            (dflogs['shotResult'] == "Made")])
        stats["FGA"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['isFieldGoal'] == 1.0)])
        stats["FTA"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['actionType'] == 'Free Throw')])
        stats["FG3M"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['isFieldGoal'] == 1.0) &
            (dflogs['shotResult'] == "Made") &
            (dflogs['shotValue'] == 3)])
        stats["FG3A"] = len(dflogs[
            (dflogs['personId'] == int(self.player_id)) &
            (dflogs['isFieldGoal'] == 1.0) &
            (dflogs['shotValue'] == 3)])

        # This ensures we don't attempt to reference a None as a string
        dflogs2['HOMEDESCRIPTION'] = dflogs2['HOMEDESCRIPTION']\
            .replace(np.nan, "")\
            .astype(str)
        dflogs2['VISITORDESCRIPTION'] = dflogs2['VISITORDESCRIPTION']\
            .replace(np.nan, "")\
            .astype(str)

        stats["REB"] = self._count_rebounds(dflogs2, self.player_id)
        stats["AST"] = self._count_assists(dflogs2, self.player_id)
        stats["STL"] = self._count_steals(dflogs2, self.player_id)
        stats["BLK"] = self._count_blocks(dflogs2, self.player_id)
        stats["TOV"] = self._count_turnovers(dflogs2, self.player_id)
        stats["STOV"] = self._count_sturnovers(dflogs2, self.player_id)

        stats["TEAM_POSS"] = self._estimate_possessions(all_logs, team_id)
        player_poss = self._estimate_possessions(dflogs, team_id)
        stats["PLAYER_POSS"] = player_poss

        opp = self.teams[(self.teams['SEASON'] == int(season) + 1) &
                         (self.teams['TEAM'] == opp_tricode)].iloc[0]
        pace = self.seasons[(self.seasons['SEASON'] == int(season) + 1)]["PACE"].iloc[0]
        stats["OPP_TS"] = opp['OPP_TS']
        stats["OPP_ADJ_TS"] = opp['ADJ_OPP_TS']
        stats["OPP_TSC"] = opp["OPP_TSC"]
        stats["OPP_STOV"] = opp["OPP_STOV"]
        stats["OPP_DRTG"] = opp['DRTG']
        stats["OPP_ADJ_DRTG"] = opp['ADJ_DRTG']
        stats["LA_PACE"] = pace

        return stats

    def _calculate_time(
        self,
        dflogs: pd.DataFrame,
        clock_string: str
    ) -> pd.DataFrame:

        dflogs.dropna(subset=[clock_string], inplace=True)
        if clock_string == 'clock':
            dflogs['minutes'] = dflogs[clock_string].str[2:4].astype(int)
            dflogs['seconds'] = dflogs[clock_string].str[5:7].astype(int)
            dflogs['ms'] = dflogs[clock_string].str[8:10].astype(int)
        else:
            dflogs['minutes'] = dflogs[clock_string].str.split(':').str[0].astype(int)
            dflogs['seconds'] = dflogs[clock_string].str.split(':').str[1].astype(int)
            dflogs['ms'] = 0
            dflogs.rename(columns={'PERIOD': 'period'}, inplace=True)

        dflogs['maxMargin'] = 10
        dflogs.loc[dflogs['minutes'] >= 5, 'maxMargin'] = 20
        dflogs.loc[dflogs['minutes'] >= 8, 'maxMargin'] = 25

        dflogs['maxTime'] = 12 * 60 * 10
        dflogs.loc[dflogs['period'] > 4, 'maxTime'] = 5 * 60 * 10

        dflogs['time'] = (np.minimum(dflogs['period'] - 1, 4) * 12 * 60 * 10) + \
            (np.maximum(0, dflogs['period'] - 5) * (5 * 60 * 10)) + \
            (dflogs['maxTime']) - ((dflogs['minutes'] * 60 * 10) + \
            (dflogs['seconds'] * 10) + (dflogs['ms'] / 10))

        return dflogs
    
    def _handle_rotations(
        self,
        dflogs: pd.DataFrame,
        dflogs2: pd.DataFrame,
        game_id: str,
        player_id: str
    ) -> tuple[pd.DataFrame, pd.DataFrame, str, str, list[int]]:

        rotation = Request(function=GameRotation, args={
            "game_id": game_id
        }).function_call()
        home_rotations = pd.DataFrame(rotation.get_data_frames()[0])
        away_rotations = pd.DataFrame(rotation.get_data_frames()[1])

        if len(away_rotations[away_rotations['PERSON_ID'] == int(player_id)]) == 0:
            dfrotation = home_rotations
            opp_team_id = away_rotations.iloc[0]['TEAM_ID']
        else:
            dfrotation = away_rotations
            opp_team_id = home_rotations.iloc[0]['TEAM_ID']

        opp_tricode = dflogs[dflogs['teamId'] == opp_team_id].iloc[0]['teamTricode']
        team_id = dfrotation[dfrotation['PERSON_ID'] == int(player_id)].iloc[0]['TEAM_ID']
        bins = dfrotation[dfrotation['PERSON_ID'] == int(player_id)]\
            [['IN_TIME_REAL', 'OUT_TIME_REAL']].values.tolist()

        dflogs, dflogs2 = self._calculate_starters(dflogs, dflogs2, home_rotations, "homeStarters")
        dflogs, dflogs2 = self._calculate_starters(dflogs, dflogs2, away_rotations, "awayStarters")

        dflogs['totalStarters'] = dflogs['homeStarters'] + dflogs['awayStarters']
        dflogs2['totalStarters'] = dflogs2['homeStarters'] + dflogs2['awayStarters']

        return (dflogs, dflogs2, team_id, opp_tricode, bins)

    def _remove_garbage_time(
        self,
        dflogs: pd.DataFrame,
        dflogs2: pd.DataFrame,
        bins: list[list[int]]
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        all_logs = dflogs.copy()

        all_logs.loc[:, 'counted'] = 1
        dflogs.loc[:, 'counted'] = 1
        dflogs2.loc[:, 'counted'] = 1

        curr = False
        curr_other = False
        for bin_ in bins:
            curr = curr | ((dflogs['time'] >= bin_[0]) & (dflogs['time'] <= bin_[1]))
            curr_other = curr_other | ((dflogs2['time'] >= bin_[0]) & (dflogs2['time'] <= bin_[1]))
        dflogs = dflogs[curr]
        dflogs2 = dflogs2[curr_other]

        all_logs_garbage_time = \
            (all_logs['period'] == 4) & \
            (all_logs['margin'] >= all_logs['maxMargin']) & \
            (all_logs['totalStarters'] <= 2)
        garbage_time = \
            (dflogs['period'] == 4) & \
            (dflogs['margin'] >= dflogs['maxMargin']) & \
            (dflogs['totalStarters'] <= 2)
        garbage_time_other = \
            (dflogs2['period'] == 4) & \
            (dflogs2['margin'] >= dflogs2['maxMargin']) & \
            (dflogs2['totalStarters'] <= 2)

        all_logs.loc[all_logs_garbage_time, 'counted'] = 0
        dflogs.loc[garbage_time, 'counted'] = 0
        dflogs2.loc[garbage_time_other, 'counted'] = 0

        all_logs.loc[:, 'counted'] = all_logs['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)
        dflogs.loc[:, 'counted'] = dflogs['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)
        dflogs2.loc[:, 'counted'] = dflogs2['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)

        all_logs = all_logs[~all_logs_garbage_time]
        dflogs = dflogs[~garbage_time]
        dflogs2 = dflogs2[~garbage_time_other]

        return all_logs, dflogs, dflogs2

    def _count_rebounds(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:

        return len(dflogs2[
            (dflogs2['PLAYER1_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('REBOUND')) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('REBOUND')))])

    def _count_assists(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:

        return len(dflogs2[
            (dflogs2['PLAYER2_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('AST')) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('AST')))])

    def _count_steals(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:

        return len(dflogs2[
            (dflogs2['PLAYER2_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('STEAL')) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('STEAL')))])

    def _count_blocks(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:

        return len(dflogs2[
            (dflogs2['PLAYER3_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('BLOCK')) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('BLOCK')))])

    def _count_turnovers(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:

        return len(dflogs2[
            (dflogs2['PLAYER1_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('Turnover')) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('Turnover')))])

    def _count_sturnovers(
        self,
        dflogs2: pd.DataFrame,
        player_id: str
    ) -> int:    

        return len(dflogs2[
            (dflogs2['PLAYER1_ID'] == int(player_id)) &
            ((dflogs2['HOMEDESCRIPTION'].str.contains('Turnover') &
            (~dflogs2['HOMEDESCRIPTION'].str.contains('Bad Pass'))) |
            (dflogs2['VISITORDESCRIPTION'].str.contains('Turnover') &
            (~dflogs2['VISITORDESCRIPTION'].str.contains('Bad Pass'))))])

    def _estimate_possessions(
        self,
        dflogs: pd.DataFrame,
        team_id: str
    ) -> float:

        fgato = len(dflogs[
            (dflogs['teamId'] == team_id) &
            ((dflogs['isFieldGoal'] == 1) |
            (dflogs['actionType'] == 'Turnover'))])
        fta = len(dflogs[
            (dflogs['teamId'] == team_id) &
            (dflogs['actionType'] == 'Free Throw')])
        oreb = len(dflogs[
            (dflogs['teamId'] == team_id) &
            (dflogs['description'].str.contains('REBOUND')) &
            (((dflogs['prevFGA'] == 1.0) |
            (dflogs['prevFTA'] == 'Free Throw'))) &
            (dflogs['prevTeam'] == team_id)])

        return 0.96 * (fgato + (0.44 * fta) - oreb)

    def _calculate_starters(
        self,
        dflogs: pd.DataFrame,
        dflogs2: pd.DataFrame,
        dfrotation: pd.DataFrame,
        team: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        starters = set(dfrotation[dfrotation['IN_TIME_REAL'] == 0]['PERSON_ID'].values)
        dfrotation['IN_TIME_REAL'] = dfrotation['IN_TIME_REAL'].astype(int)
        dfrotation['OUT_TIME_REAL'] = dfrotation['OUT_TIME_REAL'].astype(int)
        dfrotation['PERSON_ID_COPY'] = dfrotation['PERSON_ID']
        df_dict = dfrotation.set_index(["PERSON_ID_COPY", "IN_TIME_REAL", "OUT_TIME_REAL"])\
            ["PERSON_ID"].to_dict()

        lineups_changedf = dflogs[
            (dflogs['description'].str.contains("SUB: ") &
            dflogs['description'].str.contains(" FOR ")) |
            (dflogs['description'].str.contains("Start of") &
            dflogs['description'].str.contains(" Period"))
        ].copy()
        
        lineups_changedf2 = dflogs2[
            (dflogs2['HOMEDESCRIPTION'].str.contains("SUB: ") &
            dflogs2['HOMEDESCRIPTION'].str.contains(" FOR ")) |
            (dflogs2['VISITORDESCRIPTION'].str.contains("SUB: ") &
            dflogs2['VISITORDESCRIPTION'].str.contains(" FOR ")) |
            (dflogs2['NEUTRALDESCRIPTION'].str.contains("Start of") &
            dflogs2['NEUTRALDESCRIPTION'].str.contains(" Period"))
        ].copy()

        # dflogs[team] = dflogs['time'].apply(lambda x: set(
        #         (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        # dflogs2[team] = dflogs2['time'].apply(lambda x: set(
        #         (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        
        lineups_changedf[team] = lineups_changedf['time'].apply(lambda x: set(
                (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        lineups_changedf2[team] = lineups_changedf2['time'].apply(lambda x: set(
                (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))

        lineups_changedf[team] = lineups_changedf.apply(lambda x:
            len(x[team].intersection(starters)), axis=1)
        lineups_changedf2[team] = lineups_changedf2.apply(lambda x:
            len(x[team].intersection(starters)), axis=1)
        
        dflogs[team] = lineups_changedf[team]
        dflogs[team] = dflogs[team].ffill()
        
        dflogs2[team] = lineups_changedf2[team]
        dflogs2[team] = dflogs2[team].ffill()
        
        return (dflogs, dflogs2)