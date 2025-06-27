'''Player Logs Endpoint'''
import os
import numpy as np
import pandas as pd

from dans.endpoints._base import LogsEndpoint
from dans.library.parameters import SeasonType
from dans.library.nba_api_client import NBAApiClient

class PBPPlayerLogs(LogsEndpoint):
    '''Finds a player's game logs within a given range of years'''

    expected_columns = [
        'SEASON_ID',
        'Player_ID',
        'Game_ID',
        'SEASON',
        'SEASON_TYPE',
        'GAME_DATE',
        'PLAYER_NAME',
        'TEAM',
        'LOCATION',
        'MATCHUP',
        'WL',
        'MIN',
        'FGM',
        'FGA',
        'FG_PCT',
        'FG3M',
        'FG3A',
        'FG3_PCT',
        'FTM',
        'FTA',
        'FT_PCT',
        'OREB',
        'DREB',
        'REB',
        'AST',
        'STL',
        'BLK',
        'TOV',
        'PF',
        'PTS',
        'PLUS_MINUS'
    ]

    error = None

    def __init__(
        self,
        name,
        year_range,
        season_type=SeasonType.default
    ):
        self.name = name
        self.year_range = year_range
        self.season_type = season_type
        self.player_id = self._lookup(name)
        
    def bball_ref(self):
        return NotImplementedError()

    def nba_stats(self):
        
        dfs = []
        for year in range(self.year_range[0], self.year_range[1] + 1):
            
            df = NBAApiClient().get_player_game_log(player_id=self.player_id, season=year, season_type=self.season_type)
            df['SEASON'] = year
            dfs.append(df)
        
        df['SEASON_TYPE'] = self.season_type
        df['PLAYER_NAME'] = self.name
        df['TEAM'] = df['MATCHUP'].str[:3]
        df['LOCATION'] = np.where(df['MATCHUP'].str.contains('@'), '@', 'vs')
        df['MATCHUP'] = df['MATCHUP'].str[-3:]
        return pd.concat(dfs)[self.expected_columns][::-1].reset_index(drop=True)

    def _lookup(self, name):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            'data\\player_ids.csv')
        names_df = pd.read_csv(path)
        
        player = names_df[names_df["NAME"] == name]["NBA_ID"]
        if len(player) == 0:
            self.error = f"Player not found: `{name}`"
            return
        return player.iloc[0]
