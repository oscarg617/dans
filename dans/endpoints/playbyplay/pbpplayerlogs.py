'''Player Logs Endpoint'''
import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm

from dans.endpoints._base import Endpoint
from dans.library.arguments import SeasonType

from nba_api.stats.endpoints.playergamelog import PlayerGameLog
from nba_api.stats.endpoints.playergamelogs import PlayerGameLogs

pd.set_option('display.max_rows', None)

class PBPPlayerLogs(Endpoint):
    '''Finds a player's game logs within a given range of years'''

    expected_columns = [
        'SEASON_ID',
        'Player_ID',
        'Game_ID',
        'GAME_DATE',
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
    data = None
    data_frame = None

    def __init__(
        self,
        name,
        year,
        season_type=SeasonType.default
    ):
        self.name = name
        self.year = year
        self.season_type = season_type
        self.player_id = self._lookup(name)
        self.data_frame = PlayerGameLog(
            player_id=self.player_id,
            season=self.year,
            season_type_all_star=season_type
        ).get_data_frames()[0][self.expected_columns]
        

    def _lookup(self, name):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            'data\\player_ids.csv')
        names_df = pd.read_csv(path)
        
        player = names_df[names_df["NAME"] == name]["NBA_ID"]
        if len(player) == 0:
            self.error = f"Player not found: `{name}`"
            return
        return player.iloc[0]
