# BXPlayerLogs

Usage

```
from dans.endpoints.boxscore.bxplayerlogs import BXPlayerLogs
```

#### `BXPlayerLogs(name, year_range, season_type)`

### Parameters

| Parameter name |  Description      |  Type     | Example             |
|----------------|-------------------|-----------|---------------------|
| name           | Player full name  |   string  | `'Anthony Edwards'` |
| year_range     | Range of years to search for logs | inclusive-inclusive list | `[2020, 2024]` |
| season_type    | Type of season games to retrieve | SeasonType enum | `SeasonType.regular_season` or `SeasonType.playoffs` |

### Methods

#### `bball_ref()`

  Uses `basketball-reference` as the data source. Returns a Pandas Dataframe containing the player's game logs in the seasons `year_range`, containing the following columns:

  ```
['SEASON', 'DATE', 'NAME', 'TEAM', 'HOME' 'MATCHUP', 'MIN', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB' 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-',]
  ```

#### `nba_stats()`

  Uses `nba-stats` as the data source. Returns a Pandas Dataframe containing the player's game logs in the seasons `year_range`, containing the following columns:

  ```
['SEASON', 'DATE', 'NAME', 'TEAM', 'HOME' 'MATCHUP', 'MIN', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB' 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-',]
  ```
