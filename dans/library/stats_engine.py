"""
Stat processing classes
"""
from abc import ABC, abstractmethod
import pandas as pd

from dans.library.parameters import DataFormat

class StatsEngine:
    
    data_source = None

    def calculate_all_stats(self, logs: pd.DataFrame, data_format=DataFormat.default, adj_def: bool = True):

        format = self._select(data_format)

        if not format:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        box_score_stats = format.aggregate(logs)
        opp_stats = OppAggregator().aggregate(logs)
        eff_stats = EfficiencyCalculator().calculate_effiency(logs, adj_def)
        
        return box_score_stats, opp_stats, eff_stats

    def _select(self, data_format=DataFormat.default, data_source=None):
        formatters = {
            DataFormat.default: PerGameAggregator(),
            DataFormat.per_100_poss: Per100PossAggregator(),
            DataFormat.pace_adj: PaceAdjAggregator(),
            DataFormat.opp_adj: PerGameAggregator(),
            DataFormat.opp_pace_adj: PaceAdjAggregator()
        }
        
        format = formatters.get(data_format)
        if not format:
            print(f"Unsupported data format: {data_format}")
        return format

class StatAggregator(ABC):
    """Abstract class for stat aggregation"""

    box_categories = ['PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'STOV']
    eff_categories = ["OPP_TS", "OPP_ADJ_TS", "OPP_TSC", "OPP_STOV"]
    def_categories = ["DRTG", "rDRTG", "ADJ_DRTG", "rADJ_DRTG", "LA_PACE"]

    @abstractmethod
    def aggregate(self, logs: pd.DataFrame) -> dict[str, float]:
        pass

class PerGameAggregator(StatAggregator):
    """Per-Game stat aggregation"""
    
    def aggregate(self, logs: pd.DataFrame) -> dict[str, float]:
        return {cat: logs[cat].mean() for cat in self.box_categories}

class Per100PossAggregator(StatAggregator):
    """Per-100 possessions stat aggregation"""
    
    def aggregate(self, logs: pd.DataFrame) -> dict[str, float]:
        player_poss = logs["PLAYER_POSS"].sum()
        return {cat: 100 * logs[cat].sum() / player_poss for cat in self.box_categories}

class PaceAdjAggregator(StatAggregator):
    """Pace-adjusted stat aggregation"""
    
    def aggregate(self, logs: pd.DataFrame) -> dict[str, float]:
        if "TEAM_POSS" in logs.columns:
            team_poss = logs["TEAM_POSS"].sum()
            return {cat: 100 * logs[cat].sum() / team_poss for cat in self.box_categories}
        else:
            player_poss = logs["PLAYER_POSS"].sum()
            min_ratio = logs['MIN'].mean() / 48
            return {cat: 100 * min_ratio * logs[cat].sum() / player_poss for cat in self.box_categories if cat in logs.columns}


class OppAggregator(StatAggregator):
    """Opponent defense stat aggregation"""
    
    def aggregate(self, logs: pd.DataFrame) -> dict[str, float]:
        result = {}
        player_poss_col = logs["PLAYER_POSS"].copy()
        player_poss = player_poss_col.sum()
        result.update({cat: 100 * (player_poss_col * logs[cat]).sum() / player_poss for cat in self.eff_categories if cat in logs.columns})
        result.update({cat: (player_poss_col * logs[cat]).sum() / player_poss for cat in self.def_categories if cat in logs.columns})
        return result

class EfficiencyCalculator:
    """Calculates efficiency stats"""

    def calculate_effiency(self, logs: pd.DataFrame, adj_def: bool = True) -> dict[str, float]:

        pts = logs["PTS"].sum()
        tsa = logs["FGA"].sum() + 0.44 * logs["FTA"].sum()
        stov = logs["STOV"].sum() if "STOV" in logs.columns else 0

        ts_pct = 100 * pts / (2 * tsa)
        tsc_pct = 100 * pts / (2 * (tsa + stov))
        stov_pct = 100 * stov / tsa

        opp_ts_col = "OPP_ADJ_TS" if adj_def else "OPP_TS"
        player_poss_col = logs["PLAYER_POSS"].copy()
        player_poss = player_poss_col.sum()

        opp_ts = 100 * (player_poss_col * logs[opp_ts_col]).sum() / player_poss
        opp_tsc = 100 * (player_poss_col * logs["OPP_TSC"]).sum() / player_poss if "OPP_TSC" in logs.columns else 0
        opp_stov = 100 * (player_poss_col * logs["OPP_STOV"]).sum() / player_poss if "OPP_STOV" in logs.columns else 0

        return {
            'rTS%': ts_pct - opp_ts,
            'rTSC%': tsc_pct - opp_tsc,
            'rsTOV%': stov_pct - opp_stov,
            'TS%': ts_pct,
            'TSC%': tsc_pct,
            'sTOV%': stov_pct
        }
