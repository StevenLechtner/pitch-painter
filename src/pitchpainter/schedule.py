"""Parse MLB games with teams, score, and game status (inning if live game) for each game given a date."""


# pylint: disable=c-extension-no-member
import re
import threading
import requests
import statsapi
from PySide6 import QtCore
from pitchpainter.print_util import dprint


class ScheduleWorker(QtCore.QObject):
    """Get games, date, and schedule with logic to parse games by date."""

    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self):
        """Initialize object to nothing of importance."""
        super().__init__()
        self.game_pks = []
        self.schedule = None
        self.date = None
        self.schedule_str = ""
        self.stop_event = threading.Event()
        self.update_event = threading.Event()

    @QtCore.Slot()
    def run(self):
        """Set schedule of games. Ping MLB's schedule every 30 seconds to update events."""
        while not self.stop_event.is_set():
            self.set_schedule_str()
            # Wait until either 30 seconds has passed, date has been updated, or worker has been stopped
            self.update_event.wait(30)
            self.update_event.clear()
        self.finished.emit()

    def stop(self):
        """Stop this thread."""
        self.stop_event.set()
        self.update_event.set()

    def set_date(self, date: QtCore.QDate):
        """Set this object's date as a QDate and update the schedule."""
        self.date = date
        self.update_event.set()

    def set_schedule_str(self):
        """Find all MLB games for the object's date with teams, score, and game status (inning if live)."""
        if self.date is None:
            self.game_pks.clear()
            self.schedule_str = "Date provided is invalid"
            self.output.emit(self.schedule_str)
            return

        self.game_pks.clear()
        try:
            self.schedule = statsapi.schedule(date=self.date.toString("yyyy-M-d"))
        except requests.exceptions.RequestException as e:
            dprint(e)
            self.game_pks.clear()
            self.schedule_str = "Uh oh, network error!"
            self.output.emit(self.schedule_str)
            return
        if self.schedule is None or len(self.schedule) == 0:
            self.schedule_str = "No games played on " + self.date.toString("MMMM d, yyyy")
            self.output.emit(self.schedule_str)
            return
        self.schedule_str = f"Games for {self.date.toString("MMMM d, yyyy")}:\n"
        for game in self.schedule:
            self.game_pks.append(game.get("game_id", -1))
            summary = game.get("summary", "")
            date_removed = re.sub(r"^\d{4}-\d{2}-\d{2} - ", "", summary)
            self.schedule_str += f"{date_removed}\n"
        self.schedule_str = self.schedule_str.rstrip()
        self.output.emit(self.schedule_str)

    def get_game_pk(self, index):
        """Get the gamePk of the game listed in index from gamePks. -1 if index not present."""
        if not self.game_pks:
            return -1
        if index == 0:
            index = 1
        index = min(index, len(self.game_pks))
        return self.game_pks[index-1]
