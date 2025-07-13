# Data Formats

There are 5 data formats provided in this API: Per-Game, Per-100-Possessions, Pace-Adjusted, Opponent-Adjusted, and Opponent-and-Pace-Adjusted. The formulas for each are defined below:

##### Per-Game

`PTS` = Total Points / Games Played

`REB` = Total Rebounds / Games Played

`AST` = Total Assists / Games Played

##### Per-100-Possessions

`PTS` = (Total Points / Possessions Played) * 100

`REB` = (Total Rebounds / Possessions Played) * 100

`AST` = (Total Assists / Possessions Played) * 100

##### Pace-Adjusted

`PTS` = (Minutes Played / Minutes Available) * (Total Points / Possessions Played) * 100

`REB` = (Minutes Played / Minutes Available) * (Total Rebounds / Possessions Played) * 100

`AST` = (Minutes Played / Minutes Available) * (Total Assists / Possessions Played) * 100

##### Opponent-Adjusted

`PTS` = (110 / Opponent Average DRTG) * (Total Points / Games Played)

`REB` = Total Rebounds / Games Played

`AST` = Total Assists / Games Played

##### Opponent-and-Pace-Adjusted

`PTS` = (Minutes Played / Minutes Available) * (110 / Opponent Average DRTG) * (Total Points / Possessions Played) * 100

`REB` = (Minutes Played / Minutes Available) * (Total Rebounds / Possessions Played) * 100

`AST` = (Minutes Played / Minutes Available) * (Total Assists / Possessions Played) * 100

### How are 'Possessions Played' Calculated?

This API estimates the number of possessions a player plays in a game differently for nba-stats and for basketball-reference. 

NBA-stats has an endpoint that provides the number of minutes a player plays per possession, MPP, in a game. We can thus take the number of minutes a player plays in a game, and divide it by the MPP to get the number of possessions a player plays in a game.

The method used for basketball-reference is not as accurate. For this site, we instead are able to find the pace at which a game is played at in a game. Pace is defined to be the number of possessions played per 48 minutes. Thus, to find the number a possessions a player plays in a game, we can multiply the pace by the number of minutes the player plays, and divide by 48.

The reason this estimation is not accurate is that it assumes that the game is being played at the same pace for the entirety of the game.

### `playbyplay` Subpackage Approach

One important difference is that stats in this subpackage are garbage-time-filtered. The definition of garbage-time is provided by Cleaning the Glass [here](https://cleaningtheglass.com/stats/guide/garbage_time).

The formula for calculating possessions is:

`POSS` = 0.96 * (Field Goal Attempts + Turnovers - Offensive Rebounds + (0.44 * Free Throw Attempts))

The new formula for `opponent-and-pace-adjusted` stats:

`PTS` = (110 / Opponent Average DRTG) * (Total Points / Team Possessions) * (100 + Team Pace - League Pace)

`REB` = (Total Rebounds / Team Possessions) * (100 + Team Pace - League Pace)

`AST` = (Total Assists / Team Possessions) * (100 + Team Pace - League Pace)
