'''Testing boxscore player methods (NBA-Stats only).'''
import unittest
import pandas as pd

from dans.endpoints.boxscore.bxplayerstats import BXPlayerStats
from dans.endpoints.boxscore.bxplayerlogs import BXPlayerLogs
from dans.library.parameters import DataFormat, SeasonType

class TestBXNSPlayers(unittest.TestCase):
    '''Tests for each boxscore player endpoint: NBA-Stats only'''
    def test_player_game_logs(self):
        logs = BXPlayerLogs("Stephen Curry", year_range=[2015, 2017], season_type=SeasonType.playoffs).nba_stats()

        expected_columns = ['SEASON',  'SEASON_TYPE',  'GAME_DATE',  'PLAYER_NAME',  'TEAM',
                            'LOCATION',  'MATCHUP',  'WL',  'MIN',  'FGM',  'FGA',  'FG_PCT',
                            'FG3M',  'FG3A',  'FG3_PCT',  'FTM',  'FTA',  'FT_PCT',  'OREB',
                            'DREB',  'REB',  'AST',  'STL',  'BLK',  'TOV',  'PF',  'PTS',
                            'PLUS_MINUS']

        self.assertEqual(logs['PTS'].sum(), 1523)
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):
        logs = BXPlayerLogs("Kobe Bryant", year_range=[2003, 2003], season_type=SeasonType.playoffs).nba_stats()
        per_game_stats = BXPlayerStats(logs, drtg_range=[90, 100], data_format=DataFormat.default).nba_stats()
        per_poss_stats = BXPlayerStats(logs, drtg_range=[90, 100], data_format=DataFormat.per_100_poss).nba_stats()

        self.assertEqual(round(per_game_stats["PTS"].loc[0], 1), 32.3)
        self.assertEqual(round(per_poss_stats["PTS"].loc[0], 1), 38.7)

if __name__ == '__main__':
    unittest.main()
