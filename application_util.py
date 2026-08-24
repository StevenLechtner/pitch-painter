import statsapi
from PySide6 import QtCore, QtWidgets, QtGui

gamePk = []

def getScheduleStr(date: QtCore.QDate):
    gamesList = []
    gamePk.clear()
    schedule = statsapi.get('schedule', {'sportId': 1, 'date': date.toString("yyyy-M-d")})
    try:
        gameList = schedule["dates"][0]["games"]
        scheduleStr = ""
        for i in gameList:
            gamesList.append(statsapi.get('game', {'gamePk': i["gamePk"]}))
        #print(f"Games for {schedule["dates"][0]["date"]}:")
        scheduleStr += f"Games for {date.toString("MMMM d, yyyy")}:\n"
        for i in gamesList:
            #print(f"{i["gameData"]["teams"]["away"]["name"]} @ {i["gameData"]["teams"]["home"]["name"]}")
            scheduleStr += f"{i["gameData"]["teams"]["away"]["name"]} @ {i["gameData"]["teams"]["home"]["name"]}\n"
            gamePk.append(i["gamePk"])
            #print(i["gamePk"])
        #print()
        scheduleStr = scheduleStr.rstrip()
        return scheduleStr
    except:
        return "No games played on " + date.toString("MMMM d, yyyy")

def getGamePk(index):
    if index == 0:
        index = 1
    if index > len(gamePk):
        index = len(gamePk)
    return gamePk[index-1]
