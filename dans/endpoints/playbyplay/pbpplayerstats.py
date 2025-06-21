'''Player Stats Endpoint'''
import os
import pandas as pd
from tqdm import tqdm

from dans.endpoints._base import Endpoint
from dans.library.arguments import DataFormat
from dans.library.pbpprocessing import PBPProcessor
from dans.library.pbpcounter import PBPCounter
from dans.library.stataggregation import AggregatorSelector, OppAggregator, EfficiencyCalculator

pd.set_option('display.max_rows', None)

class PBPPlayerStats(Endpoint):
    
    expected_log_columns = [
        'PLAYER_ID',
        'SEASON',
        'GAME_ID',
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
        'STOV',
        'TEAM_POSS',
        'PLAYER_POSS',
        'OPP_TS',
        'OPP_ADJ_TS',
        'OPP_TSC',
        'OPP_STOV',
        'DRTG',
        'ADJ_DRTG',
        'LA_PACE'
    ]
    
    expected_agg_columns = [
        'PLAYER_ID',
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
        'STOV',
        'TEAM_POSS',
        'PLAYER_POSS',
        'rTS%',
        'rTSC%',
        'rsTOV%',
        'TS%',
        'TSC%',
        'sTOV%',
        'OPP_TS',
        'OPP_ADJ_TS',
        'OPP_TSC',
        'OPP_STOV',
        'DRTG',
        'ADJ_DRTG',
        'LA_PACE'
    ]
    
    scoring_columns = [
        'PTS',
        'rTS%',
        'rTSC%',
        'rsTOV%',
        'TS%',
        'TSC%',
        'sTOV%',
        'OPP_TS',
        'OPP_ADJ_TS',
        'OPP_TSC',
        'OPP_STOV',
        'DRTG',
        'ADJ_DRTG',
    ]

    def __init__(
        self,
        player_logs: pd.DataFrame,
        drtg_range: list
    ):
        self.player_logs = player_logs
        self.drtg_range = drtg_range
        self.stats = {}
        
        self.teams = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), "data\\nba-stats-teams.csv"))
        self.seasons = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), "data\\season-averages.csv"))

        ids = player_logs["Player_ID"].unique().tolist()
        if len(ids) > 1:
            print(f"Error: There are {len(ids)} players included in the logs. There should " + 
                  "only be 1.")

        self.player_id = ids[0] if len(ids) == 1 else None

        self._iterate_through_games()

    def aggregate_logs(self, data_format=DataFormat.default, scoring_columns_only=True, adj_def=True):

        aggregator = AggregatorSelector().select(data_format)

        if not aggregator:
            return pd.DataFrame()

        box_score_stats = aggregator.aggregate(self.data_frame)
        opp_stats = OppAggregator().aggregate(self.data_frame)
        eff_stats = EfficiencyCalculator().calculate_effiency(self.data_frame, adj_def)
        misc_stats = {
            "PLAYER_ID": self.player_id,
            "TEAM_POSS": self.data_frame["TEAM_POSS"].mean(),
            "PLAYER_POSS": self.data_frame["PLAYER_POSS"].mean()
        }

        if data_format == DataFormat.opp_adj:
            drtg = "ADJ_DRTG" if adj_def else "DRTG"
            box_score_stats["PTS"] = box_score_stats["PTS"] * (110 / opp_stats[drtg])
        elif data_format == DataFormat.opp_pace_adj:
            team_poss = self.data_frame["TEAM_POSS"].sum()
            drtg = "ADJ_DRTG" if adj_def else "DRTG"
            box_score_stats["PTS"] =  box_score_stats["PTS"] *\
                ((100 + ((team_poss / len(self.data_frame)) - (opp_stats["LA_PACE"]))) / 100) * \
                (110 / opp_stats[drtg])

        box_score_stats.update(opp_stats)
        box_score_stats.update(eff_stats)
        box_score_stats.update(misc_stats)

        stats = pd.DataFrame(box_score_stats, index=[0])

        if scoring_columns_only:
            return stats[self.scoring_columns]
        else:
            return stats[self.expected_agg_columns]

    def _iterate_through_games(self):
    
        iterator = tqdm(range(len(self.player_logs)), desc='Loading play-by-plays...', ncols=75)
        pbp_logs = []
        for i in iterator:
            player_log = self.player_logs.iloc[i]
            stats = self._player_game_stats(player_log['Game_ID'], player_log['SEASON'])
            pbp_logs.append(stats)
        
        self.data_frame = pd.DataFrame(pbp_logs)[self.expected_log_columns]

    def _player_game_stats(self, game_id: str, season: int) -> dict:

        processor = PBPProcessor()
        pbp_data =  processor.process(game_id, self.player_id)
        
        all_logs = pbp_data["all_logs"]
        pbp_v3 = pbp_data["pbp_v3"]
        pbp_v2 = pbp_data["pbp_v2"]
        team_id = pbp_data["team_id"]
        opp_tricode = pbp_data["opp_tricode"]
        
        counter = PBPCounter()
        
        stats = {
            "PLAYER_ID": self.player_id,
            "SEASON": season,
            "GAME_ID": game_id
        }
        
        box_stats = counter.count_stats(pbp_v3, pbp_v2, self.player_id)
        poss_stats = counter.count_possessions(all_logs, pbp_v3, team_id)
        opp_stats = counter.count_opp_stats(self.teams, self.seasons, season, opp_tricode)
        
        stats.update(box_stats)
        stats.update(poss_stats)
        stats.update(opp_stats)
        
        return stats
