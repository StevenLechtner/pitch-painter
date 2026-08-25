import getopt
import print_util
import statsapi
import sys
import threading
from live_game import printAllPitchesFromLiveGame
from PySide6 import QtCore, QtWidgets, QtGui

gamePk = []

class LiveGameWorker(QtCore.QObject):
    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self, gamePk):
        super().__init__()
        self.gamePk = gamePk
        self.stop_event = threading.Event()

    @QtCore.Slot()
    def run(self):
        printAllPitchesFromLiveGame(self.gamePk, self.output, self.stop_event)
        self.finished.emit()

    def stop(self):
        self.stop_event.set()

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

def usage():
    print(f"Usage: python {sys.argv[0]} [options] arguments")
    print("Options:")
    print("  -h, --help          Show this help message and exit")
    print("  -v, --verbose       Enable verbose mode")

def getOptions(args):
    options = "hvo:"
    long_options = ["help", "verbose", "output="]
    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            currentArg = currentArg.lower()
            if currentArg in ("-h", "--help"):
                print("Showing Help")
                usage()
                sys.exit(2)
            elif currentArg in ("-v", "--verbose"):
                print("Verbose flag")
                print_util.setVerbose(True)
            elif currentArg in ("-o", "--output"):
                print("Output mode:", currentVal)
    except getopt.error as err:
        print("Error in augments")
        usage()
        sys.exit(2)
