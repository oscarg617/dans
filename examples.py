'''Examples of usage.'''

from dans.endpoints.playbyplay.pbpplayerlogs import PBPPlayerLogs
from dans.endpoints.playbyplay.pbpplayerstats import PBPPlayerStats
from dans.library.arguments import DataFormat, SeasonType


logs = PBPPlayerLogs("Kobe Bryant", "2006-07", season_type=SeasonType.playoffs).get_data_frame()

print(PBPPlayerStats(logs, [80, 130]).aggregate_logs(data_format=DataFormat.opp_pace_adj))
