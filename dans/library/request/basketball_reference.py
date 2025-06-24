"""Basketball-Reference requests handler"""
import pandas as pd
from bs4 import BeautifulSoup

from dans.library.request.base import DataSource

class BasketballReferenceSource(DataSource):
    """Handler for Basketball Reference web scraping"""
    
    def can_handle(self, url: str) -> bool:
        return "basketball-reference.com" in url
    
    def get_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
    
    def get_params(self, **kwargs) -> dict:
        return {}  # No params needed for scraping
    
    def parse_response(self, response, attr_id=None) -> pd.DataFrame:
        if response.status_code != 200:
            print(f"{response.status_code} Error")
            return pd.DataFrame()
        
        try:
            html_content = response.text.replace("<!--", "").replace("-->", "")
            soup = BeautifulSoup(html_content, features="lxml")
            table = soup.find("table", attrs=attr_id)
            
            if not table:
                return pd.DataFrame()
            
            # Extract headers
            headers = []
            table_header = table.find('thead')
            if table_header:
                for header in table_header.find_all('tr'):
                    headers = [el.text.strip() for el in header.find_all('th')]
            
            # Extract rows
            rows = []
            table_body = table.find('tbody')
            if table_body:
                for row in table_body.find_all('tr'):
                    rows.append([el.text.strip() for el in row.find_all('td')])
            
            return pd.DataFrame(rows, columns=headers[1:] if headers else None)
        except Exception:
            return pd.DataFrame()
