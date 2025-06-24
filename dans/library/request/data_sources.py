from dans.library.request.base import DataSource, APISource
from dans.library.request.nba_stats import NBAStatsSource
from dans.library.request.basketball_reference import BasketballReferenceSource

class DataSourceFactory:
    """Factory to create appropriate data source handlers"""
    
    _sources = [
        NBAStatsSource(),
        BasketballReferenceSource()
    ]
    
    @classmethod
    def get_source(cls, url: str = None, function=None, args=None) -> DataSource:
        # Handle API calls
        if function is not None:
            return APISource(function, args)

        # Handle URL-based requests
        if url:
            for source in cls._sources:
                if source.can_handle(url):
                    return source

        raise ValueError(f"No handler found for URL: {url} or function: {function}")
