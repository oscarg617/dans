'''Testing play-by-play player methods (NBA-Stats only).'''
import unittest
import pandas as pd

from dans.endpoints.playbyplay.pbpplayerstats import PBPPlayerStats
from dans.endpoints.playbyplay.pbpplayerlogs import PBPPlayerLogs
from dans.library.parameters import DataFormat, SeasonType

class TestPBPPlayers(unittest.TestCase):
    '''Tests for each boxscore player endpoint: NBA-Stats only'''
    def test_player_game_logs(self):
        logs = PBPPlayerLogs("Stephen Curry", year_range=[2015, 2017], season_type=SeasonType.playoffs).nba_stats()
        
        expected_columns = ['SEASON_ID',  'Player_ID',  'Game_ID',  'SEASON',  'SEASON_TYPE',
                            'GAME_DATE',  'PLAYER_NAME',  'TEAM',  'LOCATION',  'MATCHUP',  'WL',
                            'MIN',  'FGM',  'FGA',  'FG_PCT',  'FG3M',  'FG3A',  'FG3_PCT',  'FTM',
                            'FTA',  'FT_PCT',  'OREB',  'DREB',  'REB',  'AST',  'STL',  'BLK',
                            'TOV',  'PF',  'PTS',  'PLUS_MINUS']

        self.assertEqual(logs["PTS"].sum(), 1523)
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):
        logs = PBPPlayerLogs("Kobe Bryant", year_range=[2003, 2003], season_type=SeasonType.playoffs).nba_stats()
        opp_pace_adj_stats = PBPPlayerStats(logs, drtg_range=[90, 100], data_format=DataFormat.opp_pace_adj).nba_stats()
        
        self.assertEqual(opp_pace_adj_stats["PLAYER_ID"].loc[0], 977)
        self.assertEqual(round(opp_pace_adj_stats["PTS"].loc[0], 1), 39.6)
        self.assertEqual(round(opp_pace_adj_stats["FGM"].loc[0], 1), 13.1)
        self.assertEqual(round(opp_pace_adj_stats["FGA"].loc[0], 1), 30.5)
        self.assertEqual(round(opp_pace_adj_stats["FG3M"].loc[0], 1), 2.7)
        self.assertEqual(round(opp_pace_adj_stats["FG3A"].loc[0], 1), 6.4)
        self.assertEqual(round(opp_pace_adj_stats["FTM"].loc[0], 1), 7.9)
        self.assertEqual(round(opp_pace_adj_stats["FTA"].loc[0], 1), 10.0)
        self.assertEqual(round(opp_pace_adj_stats["REB"].loc[0], 1), 5.6)
        self.assertEqual(round(opp_pace_adj_stats["AST"].loc[0], 1), 4.2)
        self.assertEqual(round(opp_pace_adj_stats["STL"].loc[0], 1), 1.2)
        self.assertEqual(round(opp_pace_adj_stats["BLK"].loc[0], 1), 0.2)
        self.assertEqual(round(opp_pace_adj_stats["TOV"].loc[0], 1), 5.0)
        self.assertEqual(round(opp_pace_adj_stats["STOV"].loc[0], 1), 3.1)
        self.assertEqual(round(opp_pace_adj_stats["TEAM_POSS"].loc[0], 1), 86.3)
        self.assertEqual(round(opp_pace_adj_stats["PLAYER_POSS"].loc[0], 1), 80.0)
        self.assertEqual(round(opp_pace_adj_stats["rTS%"].loc[0], 1), 3.2)
        self.assertEqual(round(opp_pace_adj_stats["rTSC%"].loc[0], 1), 3.9)
        self.assertEqual(round(opp_pace_adj_stats["rsTOV%"].loc[0], 1), -2.5)
        self.assertEqual(round(opp_pace_adj_stats["TS%"].loc[0], 1), 52.8)
        self.assertEqual(round(opp_pace_adj_stats["TSC%"].loc[0], 1), 48.5)
        self.assertEqual(round(opp_pace_adj_stats["sTOV%"].loc[0], 1), 8.8)
        self.assertEqual(round(opp_pace_adj_stats["OPP_TS"].loc[0], 1), 49.6)
        self.assertEqual(round(opp_pace_adj_stats["OPP_ADJ_TS"].loc[0], 1), 49.6)
        self.assertEqual(round(opp_pace_adj_stats["OPP_TSC"].loc[0], 1), 44.6)
        self.assertEqual(round(opp_pace_adj_stats["OPP_STOV"].loc[0], 1), 11.3)
        self.assertEqual(round(opp_pace_adj_stats["DRTG"].loc[0], 1), 98.1)
        self.assertEqual(round(opp_pace_adj_stats["ADJ_DRTG"].loc[0], 1), 98.0)
        self.assertEqual(round(opp_pace_adj_stats["LA_PACE"].loc[0], 1), 90.6)
        self.assertEqual(round(opp_pace_adj_stats["rDRTG"].loc[0], 1), -4.1)
        self.assertEqual(round(opp_pace_adj_stats["rADJ_DRTG"].loc[0], 1), -4.3)
