import statsapi
from PySide6 import QtCore

gamePks = []

# statsapi.schedule(date=None, start_date=None, end_date=None, team="", opponent="", sportId=1, game_id=None, season=None, include_series_status=True)
def getScheduleStr(date: QtCore.QDate):
    gamePks.clear()
    try:
        schedule = statsapi.schedule(date=date.toString("yyyy-M-d"))
        scheduleStr = f"Games for {date.toString("MMMM d, yyyy")}:\n"
        for game in schedule:
            gamePks.append(game.get("game_id", -1))
            #scheduleStr += f"{game.get("away_name", "[away_name]")} @ {game.get("home_name", "[home_name]")}\n"
            summary = game.get("summary", "")
            # FIXME: This is a bad way to remove the date from the summary string
            dateRemoved = summary.split("-")[3].lstrip()
            scheduleStr += f"{dateRemoved}\n"
        scheduleStr = scheduleStr.rstrip()
        return scheduleStr
    except:
        return "No games played on " + date.toString("MMMM d, yyyy")

def getGamePk(index):
    if index == 0:
        index = 1
    if index > len(gamePks):
        index = len(gamePks)
    return gamePks[index-1]
