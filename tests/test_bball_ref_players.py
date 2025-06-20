'''Testing player methods (BBall-Ref only).'''
import unittest
import pandas as pd

from dans.endpoints.boxscore.bxplayerstats import BXPlayerStats
from dans.endpoints.boxscore.bxplayerlogs import BXPlayerLogs
from dans.library.arguments import DataFormat, SeasonType


class TestBXPlayerStats(unittest.TestCase):
    '''Tests for each dans player endpoint: BBall-Ref only'''
    def test_player_game_logs(self):

        logs = BXPlayerLogs(
            "Stephen Curry",
            year_range=[2015, 2017],
            season_type=SeasonType.playoffs
        ).bball_ref()

        expected_columns = ['SEASON', 'SEASON_TYPE', 'DATE', 'NAME', 'TEAM', 'HOME', 'MATCHUP',
                            'MIN', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%',
                            'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']

        self.assertEqual(logs['PTS'].sum(), 1523)
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):

        logs = BXPlayerLogs(
            "Kobe Bryant",
            year_range=[2003, 2003],
            season_type=SeasonType.playoffs
        ).bball_ref()

        per_game_stats = BXPlayerStats(
            logs,
            drtg_range=[90, 100],
            data_format=DataFormat.default
        ).bball_ref()

        per_poss_stats = BXPlayerStats(
            logs,
            drtg_range=[90, 100],
            data_format=DataFormat.per_100_poss
        ).bball_ref()

        self.assertEqual(per_game_stats["PTS"].loc[0], 32.3)
        self.assertEqual(per_poss_stats["PTS"].loc[0], 39.4)

    def test_no_pace_columns_fail(self):
            
        logs = BXPlayerLogs(
            "Kareem Abdul-Jabbar",
            year_range=[1972, 1972],
            season_type=SeasonType.playoffs
        ).bball_ref()
        
        per_game_stats = BXPlayerStats(
            logs,
            drtg_range=[90, 100],
            data_format=DataFormat.pace_adj
        ).bball_ref()

        self.assertEqual(len(per_game_stats), 0)

    def test_missing_pace_values_fail(self):
            
        logs = BXPlayerLogs(
            "Kareem Abdul-Jabbar",
            year_range=[1974, 1974],
            season_type=SeasonType.regular_season
        ).bball_ref()
        
        per_game_stats = BXPlayerStats(
            logs,
            drtg_range=[95.1, 95.2],
            data_format=DataFormat.pace_adj
        ).bball_ref()
        
        self.assertEqual(len(per_game_stats), 0)

    def test_missing_pace_values_pass(self):

        logs = BXPlayerLogs(
            "Kareem Abdul-Jabbar",
            year_range=[1974, 1974]
        ).bball_ref()

        per_game_stats = BXPlayerStats(
            logs,
            drtg_range=[93.6, 93.7],
            data_format=DataFormat.pace_adj
        ).bball_ref()

        self.assertEqual(per_game_stats["PTS"].loc[0], 26.6)

if __name__ == '__main__':
    unittest.main()
