"""Parse MLB games with teams, score, and game status (inning if live game) for each game given a date."""


import re
import statsapi
import threading
from pitchpainter.print_util import dprint
from PySide6 import QtCore


class schedule_worker(QtCore.QObject):
    """Get games, date, and schedule with logic to parse games by date."""

    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self):
        """Initialize object to nothing of importance."""
        super().__init__()
        self.gamePks = []
        self.schedule = None
        self.date = None
        self.scheduleStr = ""
        self.stop_event = threading.Event()
        self.update_event = threading.Event()

    @QtCore.Slot()
    def run(self):
        """Set schedule of games. Ping MLB's schedule every 30 seconds to update events."""
        while not self.stop_event.is_set():
            self.setScheduleStr()
            # Wait until either 30 seconds has passed, date has been updated, or worker has been stopped
            self.update_event.wait(30)
            self.update_event.clear()
        self.finished.emit()

    def stop(self):
        """Stop this thread."""
        self.stop_event.set()
        self.update_event.set()

    def setDate(self, date: QtCore.QDate):
        """Set this object's date as a QDate and update the schedule."""
        self.date = date
        self.update_event.set()

    def setScheduleStr(self):
        """Find all MLB games for the object's date with teams, score, and game status (inning if live)."""
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
        except Exception as e:
            self.gamePks.clear()
            if self.schedule is None:
                self.scheduleStr = "No games played on " + self.date.toString("MMMM d, yyyy")
                self.output.emit(self.scheduleStr)

    def getGamePk(self, index):
        """Get the gamePk of the game listed in index from gamePks. -1 if index not present."""
        if not self.gamePks:
            return -1
        if index == 0:
            index = 1
        if index > len(self.gamePks):
            index = len(self.gamePks)
        return self.gamePks[index-1]
