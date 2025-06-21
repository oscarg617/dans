"""
nba_api Client
"""
import pandas as pd

from dans.library.request import Request
from nba_api.stats.endpoints.playbyplayv3 import PlayByPlayV3
from nba_api.stats.endpoints.playbyplayv2 import PlayByPlayV2
from nba_api.stats.endpoints.gamerotation import GameRotation

class NBAApiClient:
    """Wrapper for nba_api calls"""
    
    def get_play_by_play_v3(self, game_id: str) -> pd.DataFrame:
        return pd.concat(Request(function=PlayByPlayV3, args={
            "game_id": game_id
        }).function_call().get_data_frames())

    def get_play_by_play_v2(self, game_id: str) -> pd.DataFrame:
        return pd.concat(Request(function=PlayByPlayV2, args={
            "game_id": game_id
        }).function_call().get_data_frames())

    def get_rotations(self, game_id: str) -> pd.DataFrame:
        return  Request(function=GameRotation, args={
            "game_id": game_id
        }).function_call().get_data_frames()
