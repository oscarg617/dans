"""NBA-Stats requests handler"""
import requests
import pandas as pd

from dans.library.request.base import DataSource
from dans.library.request import request_params

class NBAStatsSource(DataSource):
    """Handler for NBA.com API requests"""
    
    def can_handle(self, url: str) -> bool:
        return "stats.nba.com" in url
    
    def get_headers(self) -> dict:
        return request_params._standard_header()
    
    def get_params(self, year=None, season_type=None, measure_type=None, 
                   per_mode=None, url=None, **kwargs) -> dict:
        if url and "team" in url:
            return request_params._team_advanced_params(
                measure_type, per_mode, year, season_type
            )
        return request_params._player_logs_params(
            measure_type, per_mode, year, season_type
        )
    
    def parse_response(self, response) -> pd.DataFrame:
        if response.status_code != 200:
            print(f"{response.status_code} Error")
            return pd.DataFrame()
        
        try:
            response_json = response.json()
            data_frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
            if not data_frame.empty:
                data_frame.columns = response_json['resultSets'][0]['headers']
            return data_frame
        except (KeyError, IndexError):
            return pd.DataFrame()
