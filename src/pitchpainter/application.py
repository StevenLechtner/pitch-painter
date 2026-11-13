"""PyQt Application to choose a game, view pitches, and post big plays to Threads with command line arguments."""


# pylint: disable=c-extension-no-member,no-name-in-module
import sys
from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import isValid
from pitchpainter import cli, schedule
from pitchpainter.live_game import LiveGameWorker
from pitchpainter.print_util import vprint, dprint


class ApplicationWidget(QtWidgets.QWidget):
    """PtQt application window that a user can interact with to select desired games."""

    def __init__(self):
        """Initialize the PyQt widget with schedule and live game threads, setting date to current date."""
        super().__init__()

        self.showing_game = False
        self.show_game_btn = QtWidgets.QPushButton("Select desired game...")

        self.text_widget = QtWidgets.QTextEdit()
        font = QtGui.QFont("Menlo", 12)
        font.setFixedPitch(True)
        self.text_widget.setFont(font)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.text_widget.hide()

        self.live_game_thread = None
        self.live_game_worker = None
        self.schedule_thread = None
        self.schedule_worker = None
        self.start_schedule_thread()

        self.init_game_selected()
        self.init_calendar()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.calendar)
        self.layout.addWidget(self.text_widget)
        self.layout.addWidget(self.games_widget)
        self.layout.addWidget(self.show_game_btn)

        self.show_game_btn.clicked.connect(self.toggle_game)

    @QtCore.Slot()
    def toggle_game(self):
        """Show/hide game button toggle."""
        if self.showing_game:
            self.hide_game()
            if self.live_game_thread is not None and isValid(self.live_game_thread):
                if self.live_game_thread.isRunning():
                    self.show_game_btn.setEnabled(False)
        else:
            self.show_game()

    def show_game(self):
        """Show output from a game when desired game is selected."""
        self.showing_game = True
        self.calendar.hide()
        self.games_widget.hide()
        self.text_widget.setPlainText("")
        self.text_widget.show()
        index = self.games_widget.row(self.games_widget.currentItem())
        game_pk = self.schedule_worker.getGamePk(index)
        if game_pk == -1:
            self.hide_game()
            return
        self.get_pitches(game_pk)
        self.show_game_btn.setText("Return")

    def hide_game(self):
        """Hide output from a game and return to calendar/game choose screen."""
        self.stop_live_game_thread()
        self.showing_game = False
        self.calendar.show()
        self.text_widget.hide()
        self.text_widget.setPlainText(self.calendar.selectedDate().toString("MMMM d, yyyy"))
        self.games_widget.show()
        game = self.games_widget.currentItem()
        if game is not None and game.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
            self.show_game_btn.setText(
                "View "
                + game.text()
                + " on "
                + self.calendar.selectedDate().toString("MMMM d, yyyy"))
        else:
            self.show_game_btn.setText("Select desired game...")

    # TODO: decide if this is still necessary - can maybe move to a test file?
    def get_pitches(self, game_pk):
        """Start reading from a live game."""
        # ================
        # Preset JSON file
        # ================
        # with open("tests/meadows.json", "r") as f:
        #     game = json.load(f)

        # ===============================================
        # Assumes game is completed (no threading needed)
        # ===============================================
        # game = statsapi.get('game', {'game_pk': game_pk})
        # return pitchbypitch.listAllPitchesFromGame(game)

        # ================================================
        # Print pitches for live game (threading required)
        # ================================================
        self.start_live_game_thread(game_pk)

    def start_live_game_thread(self, game_pk):
        """Start reading from a live game."""
        if self.live_game_thread is not None and isValid(self.live_game_thread):
            if self.live_game_thread.isRunning():
                self.stop_live_game_thread()
        self.live_game_thread = QtCore.QThread()
        self.live_game_worker = LiveGameWorker(game_pk)
        self.live_game_worker.moveToThread(self.live_game_thread)
        self.live_game_thread.started.connect(self.live_game_worker.run)
        self.live_game_worker.output.connect(self.update_game_output)
        self.live_game_worker.finished.connect(self.live_game_thread.quit)
        self.live_game_worker.finished.connect(self.live_game_worker.deleteLater)
        self.live_game_thread.finished.connect(self.live_game_thread.deleteLater)
        self.live_game_thread.finished.connect(self.live_game_thread_finished)
        self.live_game_thread.start()

    def start_schedule_thread(self):
        """Start reading from the MLB's schedule as a separate thread."""
        if self.schedule_thread is not None and isValid(self.schedule_thread):
            if self.schedule_thread.isRunning():
                self.stop_schedule_thread()
        self.schedule_thread = QtCore.QThread()
        self.schedule_worker = schedule.schedule_worker()
        self.schedule_worker.moveToThread(self.schedule_thread)
        self.schedule_thread.started.connect(self.schedule_worker.run)
        self.schedule_worker.output.connect(self.update_schedule_output)
        self.schedule_worker.finished.connect(self.schedule_thread.quit)
        self.schedule_worker.finished.connect(self.schedule_worker.deleteLater)
        self.schedule_thread.finished.connect(self.schedule_thread.deleteLater)
        self.schedule_thread.finished.connect(self.schedule_thread_finished)
        self.schedule_thread.start()

    def update_game_output(self, text):
        """Add text to the game print view and vprint to stdout if flagged."""
        # update text_widget with text
        self.text_widget.append(text)

        # verbose print text to console
        vprint(text)

    def update_schedule_output(self):
        """Show all games for a given date with teams, score, and status (inning if live)."""
        if not self.showing_game:
            self.text_widget.setPlainText(self.schedule_worker.scheduleStr)
            self.text_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.games_widget.clear()
        self.games_widget.addItems(self.schedule_worker.scheduleStr.split("\n"))

        header = self.games_widget.item(0)
        header.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
        label = QtWidgets.QLabel(header.text())
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        header.setText("")
        self.games_widget.setItemWidget(header, label)

    def stop_all_threads(self):
        """Stop the live game and schedule threads."""
        self.stop_live_game_thread()
        self.stop_schedule_thread()
        dprint("All threads stopped")

    def stop_live_game_thread(self):
        """Stop the live game thread worker and child threads."""
        if self.live_game_thread is not None:
            dprint("Stopping live game worker and child threads")
            self.live_game_worker.stop()
            dprint("Live game thread and child threads stopped")

        if self.live_game_thread is not None and isValid(self.live_game_thread):
            if self.live_game_thread.isRunning():
                dprint("Quitting live game thread")
                self.live_game_thread.quit()
                dprint("Waiting for live game thread")
                self.live_game_thread.wait()
                dprint("Live game thread stopped")
            else:
                dprint("Live game thread was not running")

    def stop_schedule_thread(self):
        """Stop the schedule worker thread."""
        if self.schedule_thread is not None and isValid(self.schedule_thread):
            if self.schedule_thread.isRunning():
                dprint("Stopping schedule worker")
                self.schedule_worker.stop()
                dprint("Quitting schedule thread")
                self.schedule_thread.quit()
                dprint("Waiting for schedule thread")
                self.schedule_thread.wait()
                dprint("Schedule thread stopped")

    def live_game_thread_finished(self):
        """Enable the bottom show game button when the live game thread is finished."""
        dprint("Live game output finished")
        self.show_game_btn.setEnabled(True)

    def schedule_thread_finished(self):
        """Set schedule thread and worker to None."""
        dprint("Schedule thread finished")
        self.schedule_thread = None
        self.schedule_worker = None

    def init_calendar(self):
        """Create the calendar widget and set the date to the current date."""
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.show()
        self.calendar.selectionChanged.connect(self.update_date_selected)
        self.update_date_selected()

    def update_date_selected(self):
        """Set the date in the schedule worker, which populates the games scheduled on the day."""
        date = self.calendar.selectedDate()
        self.schedule_worker.setDate(date)
        # self.schedule_worker.date = date
        # self.schedule_worker.update_event.set()

    def init_game_selected(self):
        """Create the list widget below the calendar to select a game to view."""
        self.games_widget = QtWidgets.QListWidget()
        self.games_widget.currentItemChanged.connect(self.update_game_selected)
        self.update_game_selected()

    def update_game_selected(self):
        """Update highlighed game selected and change bottom text to view the highlighed game."""
        game = self.games_widget.currentItem()
        if game is not None and game.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
            self.show_game_btn.setText(
                "View "
                + game.text()
                + " on "
                + self.calendar.selectedDate().toString("MMMM d, yyyy"))
            # print(game.text())

    # pylint: disable=invalid-name
    def closeEvent(self, event=None):
        """Stop all threads and close the application widget; QtWidget's native closeEvent call."""
        print("Application shutdown...")
        self.stop_all_threads()
        print("Done!")
        if event:
            event.accept()


def main():
    """Create the application widget. Specify the application name, window size/title, and show the widget."""
    cli.get_options(sys.argv[1:])
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pitcher Painter")

    widget = ApplicationWidget()
    widget.resize(800, 600)
    # widget.resize(1000, 1000)
    widget.setWindowTitle("Pitcher Painter")
    widget.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
