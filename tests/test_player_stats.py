'''Testing player methods.'''
import unittest

from dans.endpoints.playerstats import PlayerStats
from dans.endpoints.playerlogs import PlayerLogs
from dans.library.arguments import DataFormat, SeasonType

class TestPlayerStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def test_player_game_logs(self):

        logs = PlayerLogs(
            "Stephen Curry",
            year_range=[2015, 2017],
            season_type=SeasonType.playoffs
        ).bball_ref()

        expected_columns = ['SEASON', 'DATE', 'NAME', 'TEAM', 'HOME', 'MATCHUP', 'MIN', 'FG',
                            'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB',
                            'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']

        self.assertEqual(logs['PTS'].sum(), 1523)
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):

        per_game_stats = PlayerStats(
            "Kobe Bryant",
            year_range=[2003, 2003],
            drtg_range=[90, 100],
            data_format=DataFormat.default,
            season_type=SeasonType.playoffs
        ).bball_ref()

        per_poss_stats = PlayerStats(
            "Kobe Bryant",
            year_range=[2001, 2003],
            drtg_range=[90, 100],
            data_format=DataFormat.per_100_poss,
            season_type=SeasonType.playoffs
        ).bball_ref()

        self.assertEqual(per_game_stats["PTS"].loc[0], 32.3)
        self.assertEqual(per_poss_stats["PTS"].loc[0], 35.7)

    def test_no_pace_columns_fail(self):

        with self.assertRaises(SystemExit) as cm:
            per_game_stats = PlayerStats(
                "Kareem Abdul-Jabbar",
                year_range=[1972, 1972],
                drtg_range=[90, 100],
                data_format=DataFormat.pace_adj,
                season_type=SeasonType.playoffs
            ).bball_ref()

        self.assertEqual(cm.exception.code, 1)

    def test_missing_pace_values_fail(self):

        with self.assertRaises(SystemExit) as cm:
            per_game_stats = PlayerStats(
                "Kareem Abdul-Jabbar",
                year_range=[1974, 1974],
                drtg_range=[95.1, 95.2],
                data_format=DataFormat.pace_adj,
                season_type=SeasonType.regular_season
            ).bball_ref()

        self.assertEqual(cm.exception.code, 1)

    def test_missing_pace_values_pass(self):

        per_game_stats = PlayerStats(
            "Kareem Abdul-Jabbar",
            year_range=[1974, 1974],
            drtg_range=[93.6, 93.7],
            data_format=DataFormat.pace_adj,
            season_type=SeasonType.regular_season
        ).bball_ref()

        self.assertEqual(per_game_stats["PTS"].loc[0], 26.6)

if __name__ == '__main__':
    unittest.main()
