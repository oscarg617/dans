"""
Play-by-play counts
"""
import pandas as pd
import numpy as np

class PBPCounter:

    def count_stats(self, pbp_v3: pd.DataFrame, pbp_v2: pd.DataFrame, player_id: int) -> dict:

        stats = {}
        stats["PTS"] = self._count_pts(pbp_v3, player_id)
        stats["FGM"] = self._count_fgm(pbp_v3, player_id)
        stats["FGA"] = self._count_fga(pbp_v3, player_id)
        stats["FG3M"] = self._count_fg3m(pbp_v3, player_id)
        stats["FG3A"] = self._count_fg3a(pbp_v3, player_id)
        stats["FTM"] = self._count_ftm(pbp_v3, player_id)
        stats["FTA"] = self._count_fta(pbp_v3, player_id)

        # This ensures we don't attempt to reference a None as a string
        pbp_v2['HOMEDESCRIPTION'] = pbp_v2['HOMEDESCRIPTION'].replace(np.nan, "").astype(str)
        pbp_v2['VISITORDESCRIPTION'] = pbp_v2['VISITORDESCRIPTION'].replace(np.nan, "").astype(str)

        stats["REB"] = self._count_reb(pbp_v2, player_id)
        stats["AST"] = self._count_ast(pbp_v2, player_id)
        stats["STL"] = self._count_stl(pbp_v2, player_id)
        stats["BLK"] = self._count_blk(pbp_v2, player_id)
        stats["TOV"] = self._count_tov(pbp_v2, player_id)
        stats["STOV"] = self._count_stov(pbp_v2, player_id)
        return stats

    def count_possessions(self, all_logs: pd.DataFrame, pbp_v3: pd.DataFrame, team_id: int) -> dict:
        stats = {}
        stats["TEAM_POSS"] = self._estimate_possessions(all_logs, team_id)
        stats["PLAYER_POSS"] = self._estimate_possessions(pbp_v3, team_id)
        return stats

    def count_opp_stats(self, teams: pd.DataFrame, seasons: pd.DateOffset, season: int, opp_tricode: str):
        
        opp = teams[(teams['SEASON'] == season) & (teams['MATCHUP'] == opp_tricode)].iloc[0]
        pace = seasons[(seasons['SEASON'] == season)]["PACE"].iloc[0]
        
        categories = ["OPP_TS", "OPP_ADJ_TS", "OPP_TSC", "OPP_STOV", "DRTG", "ADJ_DRTG", "rDRTG", "rADJ_DRTG"]
        stats = {cat: opp[cat] for cat in categories}
        stats["LA_PACE"] = pace
        
        return stats

    def _count_pts(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return pbp_v3[(pbp_v3['personId'] == player_id) & (pbp_v3['shotResult'] == 'Made')]['shotValue'].sum() + \
            len(pbp_v3[(pbp_v3['personId'] == player_id) & (pbp_v3['actionType'] == 'Free Throw') & (pbp_v3['description'].str.contains('PTS'))])

    def _count_fgm(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & \
            (pbp_v3['isFieldGoal'] == 1.0) & (pbp_v3['shotResult'] == "Made")])

    def _count_fga(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & (pbp_v3['isFieldGoal'] == 1.0)])

    def _count_fg3m(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & (pbp_v3['isFieldGoal'] == 1.0) & \
            (pbp_v3['shotResult'] == "Made") & (pbp_v3['shotValue'] == 3)])

    def _count_fg3a(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & \
            (pbp_v3['isFieldGoal'] == 1.0) & (pbp_v3['shotValue'] == 3)])

    def _count_ftm(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & \
            (pbp_v3['actionType'] == 'Free Throw') & (pbp_v3['description'].str.contains('PTS'))])

    def _count_fta(self, pbp_v3: pd.DataFrame, player_id: int) -> int:
        return len(pbp_v3[(pbp_v3['personId'] == int(player_id)) & (pbp_v3['actionType'] == 'Free Throw')])

    def _count_reb(self, dflogs2: pd.DataFrame, player_id: str) -> int:
        return len(dflogs2[(dflogs2['PLAYER1_ID'] == int(player_id)) & \
            ((dflogs2['HOMEDESCRIPTION'].str.contains('REBOUND')) | (dflogs2['VISITORDESCRIPTION'].str.contains('REBOUND')))])

    def _count_ast(self, dflogs2: pd.DataFrame, player_id: str) -> int:
        return len(dflogs2[ (dflogs2['PLAYER2_ID'] == int(player_id)) & \
            ((dflogs2['HOMEDESCRIPTION'].str.contains('AST')) | (dflogs2['VISITORDESCRIPTION'].str.contains('AST')))])

    def _count_stl(self, dflogs2: pd.DataFrame, player_id: str) -> int:
        return len(dflogs2[(dflogs2['PLAYER2_ID'] == int(player_id)) & \
            ((dflogs2['HOMEDESCRIPTION'].str.contains('STEAL')) | (dflogs2['VISITORDESCRIPTION'].str.contains('STEAL')))])

    def _count_blk(self, dflogs2: pd.DataFrame, player_id: str) -> int:
        return len(dflogs2[(dflogs2['PLAYER3_ID'] == int(player_id)) & \
            ((dflogs2['HOMEDESCRIPTION'].str.contains('BLOCK')) | (dflogs2['VISITORDESCRIPTION'].str.contains('BLOCK')))])

    def _count_tov(self, dflogs2: pd.DataFrame, player_id: str) -> int:
        return len(dflogs2[ (dflogs2['PLAYER1_ID'] == int(player_id)) & \
            ((dflogs2['HOMEDESCRIPTION'].str.contains('Turnover')) | (dflogs2['VISITORDESCRIPTION'].str.contains('Turnover')))])

    def _count_stov(self, dflogs2: pd.DataFrame, player_id: str) -> int:    
        return len(dflogs2[(dflogs2['PLAYER1_ID'] == int(player_id)) & ((dflogs2['HOMEDESCRIPTION'].str.contains('Turnover') & \
            (~dflogs2['HOMEDESCRIPTION'].str.contains('Bad Pass'))) | (dflogs2['VISITORDESCRIPTION'].str.contains('Turnover') & (~dflogs2['VISITORDESCRIPTION'].str.contains('Bad Pass'))))])

    def _estimate_possessions(self, dflogs: pd.DataFrame, team_id: str) -> float:
        fgato = len(dflogs[(dflogs['teamId'] == team_id) & ((dflogs['isFieldGoal'] == 1) | (dflogs['actionType'] == 'Turnover'))])
        fta = len(dflogs[(dflogs['teamId'] == team_id) & (dflogs['actionType'] == 'Free Throw')])
        oreb = len(dflogs[(dflogs['teamId'] == team_id) & (dflogs['description'].str.contains('REBOUND')) & (((dflogs['prevFGA'] == 1.0) | (dflogs['prevFTA'] == 'Free Throw'))) & (dflogs['prevTeam'] == team_id)])
        return 0.96 * (fgato + (0.44 * fta) - oreb)
