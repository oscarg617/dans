"""
Cache
"""

import os
import pandas as pd

class Cache:

    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/cache.csv')
    logs = pd.read_csv(path, dtype={"GAME_ID": "str"}).reset_index(drop=True)

    def insert_logs(self, new_logs: pd.DataFrame):
        self.logs = pd.concat([self.logs, new_logs]).drop_duplicates(subset=["PLAYER_ID", "GAME_ID"]).reset_index(drop=True) if not self.logs.empty else new_logs
        self.logs.to_csv(self.path, index=False)

    def lookup_logs(self, player_id: int, game_ids: list[str]) -> pd.DataFrame:
        return self.logs[(self.logs["PLAYER_ID"] == player_id) & (self.logs["GAME_ID"].isin(game_ids))].copy()
