# PBPPlayerLogs

Usage

```
from dans.endpoints.playbyplay.pbpplayerlogs import PBPPlayerLogs
```

### `PBPPlayerLogs(name, year, season_type)`

### Parameters

| Parameter name |  Description      |  Type     | Example             |
|----------------|-------------------|-----------|---------------------|
| name           | Player full name  |   string  | `'Anthony Edwards'` |
| year     | Year to search for logs | int | `2024` |
| season_type    | Type of season games to retrieve | SeasonType enum | `SeasonType.regular_season` or `SeasonType.playoffs` |

#### `bball_ref()`

  The `basketball-reference` subpackage does not support play-by-play stats. This method will return a `NotImplementedError`.

#### `nba_stats()`

  Uses `nba-stats` play-by-play data as the data source. Returns a Pandas Dataframe containing the player's game logs in the seasons `year_range`, containing the following columns:

  ```
  ['SEASON_ID', 'Player_ID', 'Game_ID', 'SEASON', 'SEASON_TYPE', 'GAME_DATE', 'PLAYER_NAME', 'TEAM', 'LOCATION', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
  ```

