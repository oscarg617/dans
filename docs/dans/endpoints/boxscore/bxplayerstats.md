# BXPlayerStats

Usage

```
from dans.endpoints.boxscore.bxplayerstats import BXPlayerStats
```

#### `BXPlayerStats(player_logs, drtg_range, data_format)`

### Parameters

| Parameter name |  Description      |  Type     | Example             |
|----------------|-------------------|-----------|---------------------|
| player_logs    | DataFrame containing a player's logs |  pd.DataFrame  | |
| drtg_range     | Range of defensive strength in terms of defensive rating | inclusive-exclusive list | `[107, 112]` |
| data_format    | Type of statistical calculation applied to the raw game logs | DataFormat enum | `DataFormat.pace_adj` |

### Methods

#### `bball_ref()`

Uses `basketball-reference` as the data source. Returns a Pandas DataFrame with the player's `player_logs` aggregated using `data_format`, filtered for games against teams with defensive ratings in the specified `drtg_range`.

  ```
  ['PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST',  'STL', 'BLK', 'TOV', 'PLAYER_POSS', 'rTS%', 'TS%', 'OPP_TS', 'DRTG']
  ```

#### `nba_stats()`

Uses `nba-stats` as the data source. Returns a Pandas DataFrame with the player's `player_logs` aggregated using `data_format`, filtered for games against teams with defensive ratings in the specified `drtg_range`.

  ```
  ['PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST',  'STL', 'BLK', 'TOV', 'PLAYER_POSS', 'rTS%', 'TS%', 'OPP_TS', 'OPP_ADJ_TS', 'DRTG', 'ADJ_DRTG']
  ```

#### `get_processed_logs()`

  Returns a Pandas DataFrame with the player's logs. Includes opponent defensive metrics.

  `bball_ref()` or `nba_stats()` must be called before this method, as the processed logs are calculated during those function calls.

Columns will vary slightly depending on the data source called.

```
['PLAYER_ID', 'SEASON', 'GAME_ID', 'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'STOV', 'TEAM_POSS', 'PLAYER_POSS', 'OPP_TS', 'OPP_ADJ_TS', 'OPP_TSC', 'OPP_STOV', 'DRTG', 'ADJ_DRTG', 'rDRTG', 'rADJ_DRTG']
```

