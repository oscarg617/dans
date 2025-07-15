"""Base class for data sources"""
import json
import requests
from abc import ABC, abstractmethod
import pandas as pd
from ratelimit import sleep_and_retry, limits

from nba_api.stats.endpoints.playergamelog import PlayerGameLog
from nba_api.stats.endpoints.playbyplayv3 import PlayByPlayV3
from dans.library.request.cache.cached_args import cached_args

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def get_headers(self) -> dict:
        pass
    
    @abstractmethod
    def get_params(self, **kwargs) -> dict:
        pass
    
    @abstractmethod
    def parse_response(self, response) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass

class APISource(DataSource):
    """Handler for API calls with rate limiting"""
    
    def __init__(self, function, args):
        self.function = function
        self.args = args or {}
    
    def can_handle(self, url: str) -> bool:
        return url is None  # APIs don't use URLs
    
    def get_headers(self) -> dict:
        return {}
    
    def get_params(self, **kwargs) -> dict:
        return {}
    
    def parse_response(self, response) -> pd.DataFrame:
        # For APIs, the response is whatever the function returns
        return response

file = 0

class RateLimiter:
    """Rate limiting functionality"""
    
    file = 0
    
    @staticmethod
    @sleep_and_retry
    @limits(calls=19, period=60)
    def make_request(func, *args, **kwargs):
        
        global file
        file += 1
              
        # Check if API request is cached (for testing purposes)
        if 'headers' in kwargs and 'User-Agent' not in kwargs['headers']:
            kw_tup = kwargs.copy()
            kw_tup['headers'] = tuple(list(kw_tup['headers'].items()))
            kw_tup = tuple(list(kw_tup.items()))
            req_tup = (args, kw_tup)
            if req_tup in cached_args:
                res = cached_args[req_tup]
                return res
        
        # Check if request.get is cached (for testing purposes)
        if 'headers' in kwargs and 'User-Agent' in kwargs['headers']:
            kw_tup = kwargs.copy()
            kw_tup['headers'] = tuple(list(kw_tup['headers'].items()))
            kw_tup['params'] = tuple(list(kw_tup['params'].items()))
            kw_tup = tuple(list(kw_tup.items()))
            req_tup = (args, kw_tup)
            if req_tup in cached_args:
                res = cached_args[req_tup]
                return res
        
        if 'player_id' in kwargs and 'season' in kwargs and 'season_type_all_star' in kwargs:
            kw_tup = tuple(list(kwargs.items()))
            req_tup = (args, kw_tup)
            if req_tup in cached_args:
                res = cached_args[req_tup]
                return res
        
        if 'game_id' in kwargs:
            kw_tup = tuple(list(kwargs.items()))
            req_tup = (str(func), args, kw_tup)
            if req_tup in cached_args:
                res = cached_args[req_tup]
                return res
        
        res = func(*args, **kwargs)
        # dfs = res.get_data_frames()
        # print(dfs)
        # for df in dfs:
        #     df.to_csv(f"a{file}.txt", index=False)
        #     file += 1
        return res
