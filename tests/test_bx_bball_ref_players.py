'''Testing boxscore player methods (BBall-Ref only).'''
import unittest
import pandas as pd

from dans.endpoints.boxscore.bxplayerstats import BXPlayerStats
from dans.endpoints.boxscore.bxplayerlogs import BXPlayerLogs
from dans.library.parameters import DataFormat, SeasonType


class TestBXBRPlayers(unittest.TestCase):
    '''Tests for each boxscore player endpoint: BBall-Ref only'''
    def test_player_game_logs(self):

        logs = BXPlayerLogs("Stephen Curry", year_range=[2015, 2017], season_type=SeasonType.playoffs).bball_ref()
        print(logs)

        expected_columns = ['SEASON',  'SEASON_TYPE',  'GAME_DATE',  'PLAYER_NAME',  'TEAM',
                            'LOCATION',  'MATCHUP',  'WL',  'MIN',  'FGM',  'FGA',  'FG_PCT',
                            'FG3M',  'FG3A',  'FG3_PCT',  'FTM',  'FTA',  'FT_PCT',  'OREB',
                            'DREB',  'REB',  'AST',  'STL',  'BLK',  'TOV',  'PF',  'PTS',
                            'PLUS_MINUS']

        self.assertEqual(logs['PTS'].sum(), 1523)
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):

        logs = BXPlayerLogs("Kobe Bryant", year_range=[2003, 2003], season_type=SeasonType.playoffs).bball_ref()
        per_game_stats = BXPlayerStats(logs, drtg_range=[90, 100], data_format=DataFormat.default).bball_ref()
        per_poss_stats = BXPlayerStats(logs, drtg_range=[90, 100], data_format=DataFormat.per_100_poss).bball_ref()

        self.assertEqual(round(per_game_stats["PTS"].loc[0], 1), 32.3)
        self.assertEqual(round(per_poss_stats["PTS"].loc[0], 1), 39.4)

    def test_missing_pace_values_fail(self):
            
        logs = BXPlayerLogs("Kareem Abdul-Jabbar", year_range=[1974, 1974], season_type=SeasonType.regular_season).bball_ref()
        per_game_stats = BXPlayerStats(logs, drtg_range=[95.1, 95.2], data_format=DataFormat.pace_adj).bball_ref()
        
        self.assertEqual(len(per_game_stats), 0)

    def test_missing_pace_values_pass(self):

        logs = BXPlayerLogs("Kareem Abdul-Jabbar", year_range=[1974, 1974]).bball_ref()
        per_game_stats = BXPlayerStats(logs, drtg_range=[93.6, 93.7], data_format=DataFormat.pace_adj).bball_ref()

        self.assertEqual(round(per_game_stats["PTS"].loc[0], 1), 26.6)

if __name__ == '__main__':
    unittest.main()
