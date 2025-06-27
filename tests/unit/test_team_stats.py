'''Testing team methods.'''
import unittest

from dans.endpoints.boxscore.bxteams import BXTeams

class TestTeamStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def test_team_within_drtg(self):
        teams_df = BXTeams([2019, 2022], [105, 110]).bball_ref()
        self.assertEqual(teams_df.shape[0], 37)

        expected_columns = ['SEASON', 'MATCHUP', 'DRTG', 'OPP_TS', 'rDRTG']
        self.assertListEqual(list(teams_df.columns), expected_columns)

if __name__ == '__main__':
    unittest.main()
