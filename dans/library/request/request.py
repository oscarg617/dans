"""HTTP Request handler"""
import requests
import pandas as pd

from dans.library.request.base import RateLimiter, APISource
from dans.library.request.data_sources import DataSourceFactory
from dans.library.request.basketball_reference import BasketballReferenceSource

class Request:
    """Simplified request class using modular architecture"""
    
    def __init__(self, url: str = None, attr_id=None, function=None, args=None, **kwargs):
        self.url = url
        self.attr_id = attr_id
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.source = DataSourceFactory.get_source(url, function, args)
        self.rate_limiter = RateLimiter()
    
    def get_response(self) -> pd.DataFrame:
        """Get response using appropriate data source"""
        
        if self.kwargs and "year" in self.kwargs:
            self.kwargs["year"] = self._format_year(self.kwargs["year"])
        
        if self.args and "season" in self.args:
            self.args["season"] = self._format_year(self.args["season"])
    
        # Handle API calls
        if isinstance(self.source, APISource):
            return self._handle_function_call()
        
        # Handle URL-based requests
        return self._handle_url_request()
    
    def _handle_function_call(self) -> pd.DataFrame:
        """Handle API calls with rate limiting"""
        try:
            response = self.rate_limiter.make_function_call(
                self.source.function, 
                **self.source.args
            )
            return self.source.parse_response(response)
        except Exception as e:
            print(f"Function call failed: {e}")
            return pd.DataFrame()
    
    def _handle_url_request(self) -> pd.DataFrame:
        """Handle URL-based requests with rate limiting"""
        headers = self.source.get_headers()
        params = self.source.get_params(url=self.url, **self.kwargs)
        try:
            response = self.rate_limiter.make_request(
                requests.get,
                url=self.url,
                headers=headers,
                params=params,
                timeout=60
            )
            
            # Pass attr_id for Basketball Reference
            if isinstance(self.source, BasketballReferenceSource):
                return self.source.parse_response(response, self.attr_id)
            else:
                return self.source.parse_response(response)
                
        except Exception as e:
            print(f"Request failed: {e}")
            return pd.DataFrame()

    def _format_year(self, year):
        start_year = year - 1
        end_year_format = year % 100
        if end_year_format >= 10:
            return f'{start_year}-{end_year_format}'
        return f'{start_year}-0{end_year_format}'