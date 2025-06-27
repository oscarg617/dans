'''Player Stats Endpoint.'''
import os
import sys
import requests
import pandas as pd
from tqdm import tqdm
from typing import Optional
from bs4 import BeautifulSoup

from dans.library.parameters import SeasonType, DataFormat, Site
from dans.library.request.request import Request
from dans.endpoints._base import StatsEndpoint
from dans.endpoints.boxscore.bxteams import BXTeams
from dans.library.stats_engine import StatsEngine
from dans.library.bx_possessions import BBallRefPossCount, NBAStatsPossCount

class BXPlayerStats(StatsEndpoint):
    '''Calculates players stats against opponents within a given range of defensive strength'''
    
    expected_stat_columns = [
        'PTS',
        'FGM',
        'FGA',
        'FG3M',
        'FG3A',
        'FTM',
        'FTA',
        'REB',
        'AST', 
        'STL',
        'BLK',
        'TOV',
        'PLAYER_POSS',
        'rTS%',
        'TS%',
        'OPP_TS',
        'OPP_ADJ_TS',
        'DRTG',
        'ADJ_DRTG'
    ]

    error = None
    processed_logs = None

    def __init__(
        self,
        player_logs: pd.DataFrame,
        drtg_range: list,
        data_format=DataFormat.default,
        adj_def=True,
    ):
        self.player_logs = player_logs
        self.drtg_range = drtg_range
        self.data_format = data_format
        self.year_range = [player_logs["SEASON"].min(), player_logs["SEASON"].max()]
        self.adj_def = adj_def
        self.site_csv = None
        self.data_source = None

        season_types = player_logs["SEASON_TYPE"].unique().tolist()
        if len(season_types) > 1:
            self.season_type = "BOTH"
        else:
            self.season_type = season_types[0] if len(season_types) == 1 else None

        names = player_logs["PLAYER_NAME"].unique().tolist()
        if len(names) > 1:
            print(f"There are {len(names)} players included in the logs. This will lead to " +
                  "unexpected behavior.")

        self.name = names[0] if len(names) == 1 else None

    def bball_ref(self):
        '''Uses bball-ref to calculate player logs and team defensive metrics.'''
        self.site_csv = "data/bball-ref-teams.csv"
        self.adj_def = False
        self.data_source = Site.basketball_reference
        teams_df = BXTeams(self.year_range, self.drtg_range).bball_ref()
        poss_count = BBallRefPossCount()
        return self._calculate_stats(self.player_logs, teams_df, poss_count)

    def nba_stats(self):
        '''Uses nba-stats to calculate player logs and team defensive metrics.'''
        self.site_csv = "data/nba-stats-teams.csv"
        self.data_source = Site.nba_stats
        teams_df = BXTeams(self.year_range, self.drtg_range, self.adj_def).nba_stats()
        poss_count = NBAStatsPossCount()
        return self._calculate_stats(self.player_logs, teams_df, poss_count)

    def get_processed_logs(self):
        return self.processed_logs

    def _calculate_stats(
            self,
            logs: pd.DataFrame,
            teams_df: pd.DataFrame,
            poss_count
    ):

        if len(logs) == 0 or len(teams_df) == 0:
            self.error = "No logs found."
            return pd.DataFrame()

        drtg = 'ADJ_DRTG' if self.adj_def else 'DRTG'

        logs = pd.merge(logs, teams_df, on=['SEASON', 'MATCHUP'])
        logs = logs[(logs[drtg] >= self.drtg_range[0]) & (logs[drtg] < self.drtg_range[1])]

        logs["PLAYER_POSS"] = 0
        if self.data_format == DataFormat.pace_adj or self.data_format == DataFormat.opp_pace_adj or self.data_format == DataFormat.per_100_poss:
            poss = poss_count.count(logs)
            if poss.empty:
                return pd.DataFrame()
            logs["PLAYER_POSS"] = pd.merge(logs, poss, on=["GAME_DATE"])["POSS"]

        self.processed_logs = logs.copy()

        box_score_stats, opp_stats, eff_stats = StatsEngine().calculate_all_stats(
            logs=logs,
            data_format=self.data_format,
            adj_def=self.adj_def
        )

        misc_stats = {
            "PLAYER_POSS": logs["PLAYER_POSS"].mean()
        }

        if self.data_format == DataFormat.opp_adj or self.data_format == DataFormat.opp_pace_adj:
            box_score_stats["PTS"] *= (110 / opp_stats[drtg])

        if self.error:
            print(self.error)
            return pd.DataFrame()

        misc_stats.update(box_score_stats)
        misc_stats.update(opp_stats)
        misc_stats.update(eff_stats)
        
        stats = pd.DataFrame(misc_stats, index=[0])
        
        stat_columns = set(stats.columns)
        expected_columns = [col for col in self.expected_stat_columns if col in stat_columns]
        
        return stats[expected_columns]
