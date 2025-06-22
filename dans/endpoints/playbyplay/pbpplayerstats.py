'''Player Stats Endpoint'''
import os
import pandas as pd
from tqdm import tqdm

from dans.endpoints._base import Endpoint
from dans.library.cache import Cache
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

        games_ids = self.player_logs["Game_ID"].to_list()
        seasons = self.player_logs["SEASON"].to_list()

        # Check cache first
        cache = Cache()
        cached_logs = cache.lookup_logs(self.player_id, games_ids)
        cached_game_ids = cached_logs["GAME_ID"].to_list() if not cached_logs.empty else []

        remaining_games = [game for game in zip(games_ids, seasons) if game[0] not in cached_game_ids]

        new_logs_df = pd.DataFrame()

        if remaining_games:
            new_logs = []
            iterator = tqdm(range(len(remaining_games)), desc='Loading play-by-plays...', ncols=75)
            for i in iterator:
                stats = self._player_game_stats(remaining_games[i][0], remaining_games[i][1])
                new_logs.append(stats)

            # Convert new_logs to DataFrame only if not empty
            if new_logs:
                new_logs_df = pd.DataFrame(new_logs)[self.expected_log_columns].sort_values(by='GAME_ID')

        # Combine DataFrames, filtering out empty ones
        dfs_to_combine = [df for df in [new_logs_df, cached_logs] if not df.empty]
        self.data_frame = pd.concat(dfs_to_combine, ignore_index=True) if dfs_to_combine else pd.DataFrame()

        # Insert logs to cache
        cache.insert_logs(self.data_frame)

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
