# PBPPlayerStats

Usage

```
from dans.endpoints.playbyplay.pbpplayerstats import PBPPlayerStats
```

### `PBPPlayerStats(player_logs, drtg_range)`

### Parameters

| Parameter name |  Description      |  Type     | Example             |
|----------------|-------------------|-----------|---------------------|
| player_logs    | DataFrame containing a player's logs |  pd.DataFrame  | |
| drtg_range     | Range of defensive strength in terms of defensive rating | inclusive-exclusive list | `[107, 112]` |

### Methods

#### `bball_ref()`

  The `basketball-reference` subpackage does not support play-by-play stats. This method will return a `NotImplementedError`.

#### `nba_stats()`

Uses `nba-stats` play-by-play data as the data source. Returns a Pandas DataFrame with the player's `player_logs` aggregated using `data_format`, filtered for games against teams with defensive ratings in the specified `drtg_range`.

```
['PLAYER_ID', 'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST',  'STL', 'BLK', 'TOV', 'STOV', 'TEAM_POSS', 'PLAYER_POSS', 'rTS%', 'rTSC%', 'rsTOV%', 'TS%', 'TSC%', 'sTOV%', 'OPP_TS', 'OPP_ADJ_TS', 'OPP_TSC', 'OPP_STOV', 'DRTG', 'ADJ_DRTG', 'LA_PACE']
```

#### `get_processed_logs()`

  Uses `nba-stats` play-by-play data as the data source. Returns a Pandas DataFrame with the player's logs after play-by-play processing. Includes possession counts after removing garbage-time possessions. Also includes opponent defensive metrics.

```
['PLAYER_ID', 'SEASON', 'GAME_ID', 'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'STOV', 'TEAM_POSS', 'PLAYER_POSS', 'OPP_TS', 'OPP_ADJ_TS', 'OPP_TSC', 'OPP_STOV', 'DRTG', 'ADJ_DRTG', 'rDRTG', 'rADJ_DRTG']
```
