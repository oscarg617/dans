"""
nba_api Client
"""
import pandas as pd

from dans.library.request.request import Request
from nba_api.stats.endpoints.playbyplayv3 import PlayByPlayV3
from nba_api.stats.endpoints.playbyplayv2 import PlayByPlayV2
from nba_api.stats.endpoints.gamerotation import GameRotation

class NBAApiClient:
    """Wrapper for nba_api calls"""
    
    def get_play_by_play_v3(self, game_id: str) -> pd.DataFrame:
        return self._get_endpoint_game_id_only(game_id, PlayByPlayV3)

    def get_play_by_play_v2(self, game_id: str) -> pd.DataFrame:
        return self._get_endpoint_game_id_only(game_id, PlayByPlayV2)

    def get_rotations(self, game_id: str) -> pd.DataFrame:
        return self._get_endpoint_game_id_only(game_id, GameRotation)

    def _get_endpoint_game_id_only(self, game_id: str, endpoint) -> pd.DataFrame:
        return Request(function=endpoint, args={
            "game_id": game_id
        }).function_call().get_data_frames()
