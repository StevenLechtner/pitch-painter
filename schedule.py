import re
import statsapi
import threading
from print_util import dprint
from PySide6 import QtCore

class ScheduleWorker(QtCore.QObject):
    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.gamePks = []
        self.schedule = None
        self.date = None
        self.scheduleStr = ""
        self.stop_event = threading.Event()
        self.update_event = threading.Event()

    @QtCore.Slot()
    def run(self):
        while not self.stop_event.is_set():
            self.setScheduleStr()
            # Wait until either 30 seconds has passed, date has been updated, or worker has been stopped
            self.update_event.wait(30)
            self.update_event.clear()
        self.finished.emit()

    def stop(self):
        self.stop_event.set()
        self.update_event.set()

    def setDate(self, date: QtCore.QDate):
        self.date = date
        self.update_event.set()

    def setScheduleStr(self):
        if self.date is None:
            self.gamePks.clear()
            self.scheduleStr = "Date provided is invalid"
            self.output.emit(self.scheduleStr)
            return

        self.gamePks.clear()
        try:
            self.schedule = statsapi.schedule(date=self.date.toString("yyyy-M-d"))
            self.scheduleStr = f"Games for {self.date.toString("MMMM d, yyyy")}:\n"
            for game in self.schedule:
                # dprint(game)
                self.gamePks.append(game.get("game_id", -1))
                summary = game.get("summary", "")
                dateRemoved = re.sub(r"^\d{4}-\d{2}-\d{2} - ", "", summary)
                self.scheduleStr += f"{dateRemoved}\n"
            self.scheduleStr = self.scheduleStr.rstrip()
            self.output.emit(self.scheduleStr)
        except:
            self.gamePks.clear()
            if self.schedule is None:
                self.scheduleStr = "No games played on " + self.date.toString("MMMM d, yyyy")
                self.output.emit(self.scheduleStr)

    def getGamePk(self, index):
        if index == 0:
            index = 1
        if index > len(self.gamePks):
            index = len(self.gamePks)
        return self.gamePks[index-1]
