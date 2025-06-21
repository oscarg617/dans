"""
Stat processing classes
"""
from abc import ABC, abstractmethod
import pandas as pd

from dans.library.arguments import DataFormat

class AggregatorSelector:
    
    def select(self, data_format=DataFormat.default):
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
    opp_eff_categories = ["OPP_TS", "OPP_ADJ_TS", "OPP_TSC", "OPP_STOV"]
    opp_categories = ["DRTG", "ADJ_DRTG", "LA_PACE"]

    @abstractmethod
    def aggregate(self, stats: pd.DataFrame) -> dict[str, float]:
        pass

class PerGameAggregator(StatAggregator):
    """Per-Game stat aggregation"""
    
    def aggregate(self, stats: pd.DataFrame) -> dict[str, float]:
        return {cat: stats[cat].mean() for cat in self.box_categories}

class Per100PossAggregator(StatAggregator):
    """Per-100 possessions stat aggregation"""
    
    def aggregate(self, stats: pd.DataFrame) -> dict[str, float]:
        player_poss = stats["PLAYER_POSS"].sum()
        return {cat: 100 * stats[cat].sum() / player_poss for cat in self.box_categories}
    
class PaceAdjAggregator(StatAggregator):
    """Pace-adjusted stat aggregation"""
    
    def aggregate(self, stats: pd.DataFrame) -> dict[str, float]:
        team_poss = stats["TEAM_POSS"].sum()
        return {cat: 100 * stats[cat].sum() / team_poss for cat in self.box_categories}

class OppAggregator(StatAggregator):
    """Opponent defense stat aggregation"""
    
    def aggregate(self, stats: pd.DataFrame) -> dict[str, float]:
        result = {}
        player_poss_col = stats["PLAYER_POSS"].copy()
        player_poss = player_poss_col.sum()
        result.update({cat: 100 * (player_poss_col * stats[cat]).sum() / player_poss for cat in self.opp_eff_categories})
        result.update({cat: (player_poss_col * stats[cat]).sum() / player_poss for cat in self.opp_categories})
        return result

class EfficiencyCalculator:
    """Calculates efficiency stats"""

    def calculate_effiency(self, stats: pd.DataFrame, adj_def: bool = True) -> dict[str, float]:

        pts = stats["PTS"].sum()
        tsa = stats["FGA"].sum() + 0.44 * stats["FTA"].sum()
        stov = stats["STOV"].sum()

        ts_pct = 100 * pts / (2 * tsa)
        tsc_pct = 100 * pts / (2 * (tsa + stov))
        stov_pct = 100 * stov / tsa

        opp_ts_col = "OPP_ADJ_TS" if adj_def else "OPP_TS"
        player_poss_col = stats["PLAYER_POSS"].copy()
        player_poss = player_poss_col.sum()

        opp_ts = 100 * (player_poss_col * stats[opp_ts_col]).sum() / player_poss
        opp_tsc = 100 * (player_poss_col * stats["OPP_TSC"]).sum() / player_poss
        opp_stov = 100 * (player_poss_col * stats["OPP_STOV"]).sum() / player_poss

        return {
            'rTS%': ts_pct - opp_ts,
            'rTSC%': tsc_pct - opp_tsc,
            'rsTOV%': stov_pct - opp_stov,
            'TS%': ts_pct,
            'TSC%': tsc_pct,
            'sTOV%': stov_pct
        }
