import json
import pandas as pd

from dans.library.request.cache.mock_response import MockResponse, MockAPIResponse

def read_file(file_name: str) -> str:
    with open(file_name, "r", encoding='utf-8') as file:
        return json.load(file)

def read_df(file_names: list[str]) -> list[pd.DataFrame]:
    dfs = []
    for file_name in file_names:
        dfs.append(pd.read_csv(file_name, dtype={"Game_ID": "str", "GAME_ID": "str", "gameId": "str", "scoreAway": "object", "scoreHome": "object"}))
    return dfs

cached_args = {
    (
        (),
        (('url', 'https://stats.nba.com/stats/playergamelogs'), ('headers', (('accept', 'application/json, text/plain,*/*'), ('accept-encoding', 'gzip, deflate, br'), ('accept-language', 'en-US,en;q=0.9'), ('origin', 'https://www.nba.com'), ('referer', 'https://www.nba.com/'), ('sec-fetch-dest', 'empty'), ('sec-fetch-mode', 'cors'), ('sec-fetch-site', 'same-site'), ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'))), ('params', (('DateFrom', ''), ('DateTo', ''), ('GameSegment', ''), ('LastNGames', ''), ('LeagueID', ''), ('Location', ''), ('MeasureType', None), ('Month', ''), ('OpponentTeamID', None), ('Outcome', ''), ('PORound', ''), ('PerMode', 'PerGame'), ('Period', ''), ('PlayerID', ''), ('Season', '2014-15'), ('SeasonSegment', ''), ('SeasonType', 'Playoffs'), ('ShotClockRange', ''), ('TeamID', ''), ('VsConference', ''), ('VsDivision', ''))), ('timeout', 10))
    ) :
        MockResponse(status_code=200, json_data=read_file('dans/library/request/cache/data/SC2015.txt')),
    (
        (),
        (('url', 'https://stats.nba.com/stats/playergamelogs'), ('headers', (('accept', 'application/json, text/plain,*/*'), ('accept-encoding', 'gzip, deflate, br'), ('accept-language', 'en-US,en;q=0.9'), ('origin', 'https://www.nba.com'), ('referer', 'https://www.nba.com/'), ('sec-fetch-dest', 'empty'), ('sec-fetch-mode', 'cors'), ('sec-fetch-site', 'same-site'), ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'))), ('params', (('DateFrom', ''), ('DateTo', ''), ('GameSegment', ''), ('LastNGames', ''), ('LeagueID', ''), ('Location', ''), ('MeasureType', None), ('Month', ''), ('OpponentTeamID', None), ('Outcome', ''), ('PORound', ''), ('PerMode', 'PerGame'), ('Period', ''), ('PlayerID', ''), ('Season', '2015-16'), ('SeasonSegment', ''), ('SeasonType', 'Playoffs'), ('ShotClockRange', ''), ('TeamID', ''), ('VsConference', ''), ('VsDivision', ''))), ('timeout', 10))
    ) :
        MockResponse(status_code=200, json_data=read_file('dans/library/request/cache/data/SC2016.txt')),
    (
        (),
        (('url', 'https://stats.nba.com/stats/playergamelogs'), ('headers', (('accept', 'application/json, text/plain,*/*'), ('accept-encoding', 'gzip, deflate, br'), ('accept-language', 'en-US,en;q=0.9'), ('origin', 'https://www.nba.com'), ('referer', 'https://www.nba.com/'), ('sec-fetch-dest', 'empty'), ('sec-fetch-mode', 'cors'), ('sec-fetch-site', 'same-site'), ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'))), ('params', (('DateFrom', ''), ('DateTo', ''), ('GameSegment', ''), ('LastNGames', ''), ('LeagueID', ''), ('Location', ''), ('MeasureType', None), ('Month', ''), ('OpponentTeamID', None), ('Outcome', ''), ('PORound', ''), ('PerMode', 'PerGame'), ('Period', ''), ('PlayerID', ''), ('Season', '2016-17'), ('SeasonSegment', ''), ('SeasonType', 'Playoffs'), ('ShotClockRange', ''), ('TeamID', ''), ('VsConference', ''), ('VsDivision', ''))), ('timeout', 10))
    ) :
        MockResponse(status_code=200, json_data=read_file('dans/library/request/cache/data/SC2017.txt')),
    (
        (),
        (('url', 'https://stats.nba.com/stats/playergamelogs'), ('headers', (('accept', 'application/json, text/plain,*/*'), ('accept-encoding', 'gzip, deflate, br'), ('accept-language', 'en-US,en;q=0.9'), ('origin', 'https://www.nba.com'), ('referer', 'https://www.nba.com/'), ('sec-fetch-dest', 'empty'), ('sec-fetch-mode', 'cors'), ('sec-fetch-site', 'same-site'), ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'))), ('params', (('DateFrom', ''), ('DateTo', ''), ('GameSegment', ''), ('LastNGames', ''), ('LeagueID', ''), ('Location', ''), ('MeasureType', None), ('Month', ''), ('OpponentTeamID', None), ('Outcome', ''), ('PORound', ''), ('PerMode', 'PerGame'), ('Period', ''), ('PlayerID', ''), ('Season', '2002-03'), ('SeasonSegment', ''), ('SeasonType', 'Playoffs'), ('ShotClockRange', ''), ('TeamID', ''), ('VsConference', ''), ('VsDivision', ''))), ('timeout', 10))
    ) :
        MockResponse(status_code=200, json_data=read_file('dans/library/request/cache/data/KB2003.txt')),
    (
        (),
        (('url', 'https://stats.nba.com/stats/playergamelogs'), ('headers', (('accept', 'application/json, text/plain,*/*'), ('accept-encoding', 'gzip, deflate, br'), ('accept-language', 'en-US,en;q=0.9'), ('origin', 'https://www.nba.com'), ('referer', 'https://www.nba.com/'), ('sec-fetch-dest', 'empty'), ('sec-fetch-mode', 'cors'), ('sec-fetch-site', 'same-site'), ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'))), ('params', (('DateFrom', ''), ('DateTo', ''), ('GameSegment', ''), ('LastNGames', ''), ('LeagueID', ''), ('Location', ''), ('MeasureType', 'Advanced'), ('Month', ''), ('OpponentTeamID', None), ('Outcome', ''), ('PORound', ''), ('PerMode', None), ('Period', ''), ('PlayerID', ''), ('Season', '2002-03'), ('SeasonSegment', ''), ('SeasonType', 'Playoffs'), ('ShotClockRange', ''), ('TeamID', ''), ('VsConference', ''), ('VsDivision', ''))), ('timeout', 10))
    ) :
        MockResponse(status_code=200, json_data=read_file('dans/library/request/cache/data/KB2003_adv.txt')),
    (
        (),
        (('player_id', 201939), ('season', '2014-15'), ('season_type_all_star', 'Playoffs'))
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/SC2015_pbp.txt"])),
    (
        (),
        (('player_id', 201939), ('season', '2015-16'), ('season_type_all_star', 'Playoffs'))
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/SC2016_pbp.txt"])),
    (
        (),
        (('player_id', 201939), ('season', '2016-17'), ('season_type_all_star', 'Playoffs'))
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/SC2017_pbp.txt"])),
    (
        (),
        (('player_id', 977), ('season', '2002-03'), ('season_type_all_star', 'Playoffs'))
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003_pbplogs3.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200221'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G1_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G1_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200221'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G1_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G1_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200221'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G1_gr_1.txt", "dans/library/request/cache/data/KB2003G1_gr_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200222'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G2_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G2_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200222'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G2_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G2_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200222'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G2_gr_1.txt", "dans/library/request/cache/data/KB2003G2_gr_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200223'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G3_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G3_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200223'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G3_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G3_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200223'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G3_gr_1.txt", "dans/library/request/cache/data/KB2003G3_gr_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200224'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G4_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G4_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200224'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G4_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G4_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200224'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G4_gr_1.txt", "dans/library/request/cache/data/KB2003G4_gr_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200225'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G5_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G5_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200225'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G5_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G5_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200225'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G5_gr_1.txt", "dans/library/request/cache/data/KB2003G5_gr_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv3.PlayByPlayV3'>",
        (),
        (('game_id', '0040200226'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G6_pbpv3_1.txt", "dans/library/request/cache/data/KB2003G6_pbpv3_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.playbyplayv2.PlayByPlayV2'>",
        (),
        (('game_id', '0040200226'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G6_pbpv2_1.txt", "dans/library/request/cache/data/KB2003G6_pbpv2_2.txt"])),
    (
        "<class 'nba_api.stats.endpoints.gamerotation.GameRotation'>",
        (),
        (('game_id', '0040200226'),)
    ) :
        MockAPIResponse(data_frames=read_df(["dans/library/request/cache/data/KB2003G6_gr_1.txt", "dans/library/request/cache/data/KB2003G6_gr_2.txt"])),

}
