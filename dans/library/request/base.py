"""Base class for data sources"""
from abc import ABC, abstractmethod
import pandas as pd
from ratelimit import sleep_and_retry, limits

from nba_api.stats.endpoints.playergamelog import PlayerGameLog

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

class RateLimiter:
    """Rate limiting functionality"""
    
    @staticmethod
    @sleep_and_retry
    @limits(calls=19, period=60)
    def make_request(func, *args, **kwargs):
        return func(*args, **kwargs)
    
    @staticmethod
    @sleep_and_retry
    @limits(calls=19, period=60)
    def make_function_call(func, **kwargs):
        """Rate-limited wrapper for custom function calls"""
        return func(**kwargs)
