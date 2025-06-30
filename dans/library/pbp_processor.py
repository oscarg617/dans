"""
Play-by-play processing
"""
import pandas as pd
import numpy as np

from dans.library.nba_api_client import NBAApiClient

class PBPProcessor:
    """Processes data for play-by-play data"""

    def process(self, game_id: str, player_id: str) -> dict:

        nba_api_client = NBAApiClient()

        # Two play-by-play logs are required. The V3 provides details relevant for scoring
        # stats, whereas V2 is more in depth with non-scoring plays.
        pbp_v3 = nba_api_client.get_play_by_play_v3(game_id)
        pbp_v2 = nba_api_client.get_play_by_play_v2(game_id)
        rotations = nba_api_client.get_rotations(game_id)

        # Show scores for each play
        for score_team in ['scoreHome', 'scoreAway']:
            pbp_v3[score_team] = pbp_v3[score_team]\
                .replace(r'^\s*$', "0", regex=True)\
                .replace("0", np.nan)\
                .ffill()\
                .replace(np.nan, "0")\
                .astype(int)

        # Show margin for each play
        pbp_v3['margin'] = abs(pbp_v3['scoreAway'] - pbp_v3['scoreHome'])
        pbp_v2['margin'] = pbp_v2['SCOREMARGIN']\
            .replace("0", np.nan)\
            .ffill()\
            .replace(np.nan, "0")\
            .replace("TIE", "0")\
            .astype(int)
        
        # Calculate time for each play in pbp data
        pbp_v3 = self._calculate_time(pbp_v3, 'clock')
        pbp_v2 = self._calculate_time(pbp_v2, 'PCTIMESTRING')

        # This is used to determine if a rebound is an offensive rebound.
        # This happens before any rows are eliminated so that we always know
        # what events actually happened right before a rebound occurs.
        pbp_v3['prevTeam'] = pbp_v3['teamId'].shift(1)
        pbp_v3['prevFGA'] = pbp_v3['isFieldGoal'].shift(1)
        pbp_v3['prevFTA'] = pbp_v3['actionType'].shift(1)
        
        # Calculate rotations for each play
        pbp_v3, pbp_v2, team_id, opp_tricode, bins  = self._handle_rotations(pbp_v3, pbp_v2, rotations, player_id)

        # Remove garbage time
        all_logs, pbp_v3, pbp_v2 = self._remove_garbage_time(pbp_v3, pbp_v2, bins)

        # stats = {
        #     "PLAYER_ID": self.player_id,
        #     "SEASON": season,
        #     "GAME_ID": game_id
        # }

        return {
            "all_logs": all_logs,
            "pbp_v3": pbp_v3,
            "pbp_v2": pbp_v2,
            "team_id": team_id,
            "opp_tricode": opp_tricode
        }

    def _calculate_time(self, df: pd.DataFrame, clock_col: str) -> pd.DataFrame:
        
        df.dropna(subset=[clock_col], inplace=True)
        if clock_col == 'clock':
            df['minutes'] = df[clock_col].str[2:4].astype(int)
            df['seconds'] = df[clock_col].str[5:7].astype(int)
            df['ms'] = df[clock_col].str[8:10].astype(int)
        else:
            df['minutes'] = df[clock_col].str.split(':').str[0].astype(int)
            df['seconds'] = df[clock_col].str.split(':').str[1].astype(int)
            df['ms'] = 0
            df.rename(columns={'PERIOD': 'period'}, inplace=True)

        df['maxMargin'] = 10
        df.loc[df['minutes'] >= 5, 'maxMargin'] = 20
        df.loc[df['minutes'] >= 8, 'maxMargin'] = 25

        df['maxTime'] = 12 * 60 * 10
        df.loc[df['period'] > 4, 'maxTime'] = 5 * 60 * 10

        df['time'] = (np.minimum(df['period'] - 1, 4) * 12 * 60 * 10) + \
            (np.maximum(0, df['period'] - 5) * (5 * 60 * 10)) + \
            (df['maxTime']) - ((df['minutes'] * 60 * 10) + \
            (df['seconds'] * 10) + (df['ms'] / 10))

        return df

    def _handle_rotations(self, pbp_v3: pd.DataFrame, pbp_v2: pd.DataFrame, rotations: list[pd.DataFrame], player_id: str) \
        -> tuple[pd.DataFrame, pd.DataFrame, str, str, list[int]]:

        home_rotations = rotations[0]
        away_rotations = rotations[1]

        if len(away_rotations[away_rotations['PERSON_ID'] == int(player_id)]) == 0:
            dfrotation = home_rotations
            opp_team_id = away_rotations.iloc[0]['TEAM_ID']
        else:
            dfrotation = away_rotations
            opp_team_id = home_rotations.iloc[0]['TEAM_ID']

        opp_tricode = pbp_v3[pbp_v3['teamId'] == opp_team_id].iloc[0]['teamTricode']
        team_id = dfrotation[dfrotation['PERSON_ID'] == int(player_id)].iloc[0]['TEAM_ID']
        bins = dfrotation[dfrotation['PERSON_ID'] == int(player_id)]\
            [['IN_TIME_REAL', 'OUT_TIME_REAL']].values.tolist()

        pbp_v3, pbp_v2 = self._calculate_starters(pbp_v3, pbp_v2, home_rotations, "homeStarters")
        pbp_v3, pbp_v2 = self._calculate_starters(pbp_v3, pbp_v2, away_rotations, "awayStarters")

        pbp_v3['totalStarters'] = pbp_v3['homeStarters'] + pbp_v3['awayStarters']
        pbp_v2['totalStarters'] = pbp_v2['homeStarters'] + pbp_v2['awayStarters']

        return (pbp_v3, pbp_v2, team_id, opp_tricode, bins)

    def _remove_garbage_time(self, pbp_v3: pd.DataFrame, pbp_v2: pd.DataFrame, bins: list[list[int]]) \
        -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        all_logs = pbp_v3.copy()
        

        all_logs.loc[:, 'counted'] = 1
        pbp_v3.loc[:, 'counted'] = 1
        pbp_v2.loc[:, 'counted'] = 1
        

        curr = False
        curr_other = False
        for bin_ in bins:
            curr = curr | ((pbp_v3['time'] >= bin_[0]) & (pbp_v3['time'] <= bin_[1]))
            curr_other = curr_other | ((pbp_v2['time'] >= bin_[0]) & (pbp_v2['time'] <= bin_[1]))
        pbp_v3 = pbp_v3[curr]
        pbp_v2 = pbp_v2[curr_other]
        
        all_logs_garbage_time = \
            (all_logs['period'] == 4) & \
            (all_logs['margin'] >= all_logs['maxMargin']) & \
            (all_logs['totalStarters'] <= 2)
        garbage_time = \
            (pbp_v3['period'] == 4) & \
            (pbp_v3['margin'] >= pbp_v3['maxMargin']) & \
            (pbp_v3['totalStarters'] <= 2)
        garbage_time_other = \
            (pbp_v2['period'] == 4) & \
            (pbp_v2['margin'] >= pbp_v2['maxMargin']) & \
            (pbp_v2['totalStarters'] <= 2)

    
        all_logs.loc[all_logs_garbage_time, 'counted'] = 0
        pbp_v3.loc[garbage_time, 'counted'] = 0
        pbp_v2.loc[garbage_time_other, 'counted'] = 0
        

        all_logs.loc[:, 'counted'] = all_logs['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)
        pbp_v3.loc[:, 'counted'] = pbp_v3['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)
        pbp_v2.loc[:, 'counted'] = pbp_v2['counted'].replace(0, np.nan).bfill().replace(np.nan, 0)

        all_logs = all_logs[~all_logs_garbage_time]
        pbp_v3 = pbp_v3[~garbage_time]
        pbp_v2 = pbp_v2[~garbage_time_other]

        return all_logs, pbp_v3, pbp_v2

    def _calculate_starters(self, pbp_v3: pd.DataFrame, pbp_v2: pd.DataFrame, dfrotation: pd.DataFrame, team: str) \
        -> tuple[pd.DataFrame, pd.DataFrame]:

        starters = set(dfrotation[dfrotation['IN_TIME_REAL'] == 0]['PERSON_ID'].values)
        dfrotation['IN_TIME_REAL'] = dfrotation['IN_TIME_REAL'].astype(int)
        dfrotation['OUT_TIME_REAL'] = dfrotation['OUT_TIME_REAL'].astype(int)
        dfrotation['PERSON_ID_COPY'] = dfrotation['PERSON_ID']
        df_dict = dfrotation.set_index(["PERSON_ID_COPY", "IN_TIME_REAL", "OUT_TIME_REAL"])\
            ["PERSON_ID"].to_dict()

        lineups_changedf = pbp_v3[
            (pbp_v3['description'].str.contains("SUB: ") &
            pbp_v3['description'].str.contains(" FOR ")) |
            (pbp_v3['description'].str.contains("Start of") &
            pbp_v3['description'].str.contains(" Period"))
        ].copy()
        
        lineups_changedf2 = pbp_v2[
            (pbp_v2['HOMEDESCRIPTION'].str.contains("SUB: ") &
            pbp_v2['HOMEDESCRIPTION'].str.contains(" FOR ")) |
            (pbp_v2['VISITORDESCRIPTION'].str.contains("SUB: ") &
            pbp_v2['VISITORDESCRIPTION'].str.contains(" FOR ")) |
            (pbp_v2['NEUTRALDESCRIPTION'].str.contains("Start of") &
            pbp_v2['NEUTRALDESCRIPTION'].str.contains(" Period"))
        ].copy()

        # pbp_v3[team] = pbp_v3['time'].apply(lambda x: set(
        #         (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        # pbp_v2[team] = pbp_v2['time'].apply(lambda x: set(
        #         (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        
        lineups_changedf[team] = lineups_changedf['time'].apply(lambda x: set(
                (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))
        lineups_changedf2[team] = lineups_changedf2['time'].apply(lambda x: set(
                (player for bounds, player in df_dict.items() if x in range(*bounds[1:]))))

        lineups_changedf[team] = lineups_changedf.apply(lambda x:
            len(x[team].intersection(starters)), axis=1)
        lineups_changedf2[team] = lineups_changedf2.apply(lambda x:
            len(x[team].intersection(starters)), axis=1)
        
        pbp_v3[team] = lineups_changedf[team]
        pbp_v3[team] = pbp_v3[team].ffill()
        
        pbp_v2[team] = lineups_changedf2[team]
        pbp_v2[team] = pbp_v2[team].ffill()
        
        return (pbp_v3, pbp_v2)
