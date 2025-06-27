'''Teams Endpoint'''
import os
import pandas as pd

from dans.endpoints._base import LogsEndpoint

class BXTeams(LogsEndpoint):
    '''Endpoint for finding teams with defensive strength that falls within a desired range'''

    expected_columns = [
        "SEASON",
        "TEAM",
        "DRTG",
        "OPP_TS"
    ]

    def __init__(
        self,
        year_range,
        drtg_range,
        adj_def=True,
    ):
        self.year_range = year_range
        self.drtg_range = drtg_range
        self.path = None
        self.adj_def = adj_def

    def bball_ref(self):
        '''Reads bball-ref team data and return teams that falls within self.drtg_range'''
        self.path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                     'data/bball-ref-teams.csv')
        self.adj_def = False
        return self._read_path()

    def nba_stats(self):
        '''Reads nba-stats team data and return teams that falls within self.drtg_range'''
        self.path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                     'data/nba-stats-teams.csv')
        return self._read_path()

    def _read_path(self):
        teams_df = pd.read_csv(self.path).drop(columns="Unnamed: 0")
        
        
        drtg = "ADJ_DRTG" if self.adj_def else "DRTG"
        
        teams_df = teams_df[
            (teams_df["SEASON"] >= self.year_range[0]) &
            (teams_df["SEASON"] <= self.year_range[1]) &
            (teams_df[drtg] >= self.drtg_range[0]) &
            (teams_df[drtg] < self.drtg_range[1])]

        return teams_df
