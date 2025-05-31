'''Sending Requests through HTTP'''
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from ratelimit import sleep_and_retry, limits

from dans.library import parameters

class Request:
    '''Class used for sending requests'''

    def __init__(
        self,
        url,
        attr_id=None,
        function=None,
        year=None,
        season_type=None,
        measure_type=None,
        per_mode=None
    ):
        self.function = function
        self.url = url
        self.attr_id = attr_id
        self.headers = None

        if function is None:
            self.function = requests.get

        if "stats.nba.com" in self.url:
            self.headers = parameters._standard_header()

        if "team" in self.url:
            self.params = parameters\
                ._team_advanced_params(measure_type, per_mode, year, season_type)
        else:
            self.params = parameters\
                ._player_logs_params(measure_type, per_mode, year, season_type)
        

    def get_response(self):
        '''Send request based on url'''
        if "basketball-reference.com" in self.url:
            return self._bball_ref_response()
        if "stats.nba.com" in self.url:
            return self._nba_stats_response()
        return pd.DataFrame()

    def _bball_ref_response(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        response = self.get_wrapper()
        if not response:
            return pd.DataFrame()
        
        response = response.text.replace("<!--","").replace("-->","")
        soup = BeautifulSoup(response, features="lxml")
        table = soup.find("table", attrs=self.attr_id)
        
        headers = []
        table_header = table.find('thead')
        for header in table_header.find_all('tr'):
            headers = [el.text.strip() for el in header.find_all('th')]

        rows = []
        table_body = table.find('tbody')
        for row in table_body.find_all('tr'):
            rows.append([el.text.strip() for el in row.find_all('td')])

        return pd.DataFrame(rows, columns=headers[1:])

    def _nba_stats_response(self):
        response = self.get_wrapper()
        if not response:
            return pd.DataFrame()

        response_json = response.json()
        data_frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])

        if data_frame.empty:
            return data_frame
        data_frame.columns = response_json['resultSets'][0]['headers']
        return data_frame

    @sleep_and_retry
    @limits(calls=19, period=60)
    def get_wrapper(self):
        '''Wrapper used to limit HTTP calls.'''

        if not self.headers:
            self.headers = {}

        response = \
            self.function(url=self.url, headers=self.headers, params=self.params, timeout=10)
        if response.status_code != 200:
            print(f"{response.status_code} Error")
            return
        return response
