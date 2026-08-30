import cli
import schedule
import sys
from live_game import LiveGameWorker
from print_util import vprint, dprint
from PySide6 import QtCore, QtWidgets, QtGui

class ApplicationWidget(QtWidgets.QWidget):
    #scheduleDateChanged = QtCore.Signal(QtCore.QDate)

    def __init__(self):
        super().__init__()

        self.showingGame = False
        self.showGameBtn = QtWidgets.QPushButton("Select desired game...")

        self.text_widget = QtWidgets.QTextEdit()
        font = QtGui.QFont("Menlo", 12)
        font.setFixedPitch(True)
        self.text_widget.setFont(font)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.text_widget.hide()

        self.liveGameThread = None
        self.liveGameWorker = None
        self.scheduleThread = None
        self.scheduleWorker = None
        self.startScheduleThread()

        self.initGameSelected()
        self.initCalander()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.calendar)
        self.layout.addWidget(self.text_widget)
        self.layout.addWidget(self.gamesWidget)
        self.layout.addWidget(self.showGameBtn)

        self.showGameBtn.clicked.connect(self.toggleGame)

    @QtCore.Slot()
    def toggleGame(self):
        if self.showingGame:
            self.hideGame()
            if self.liveGameThread is not None and self.liveGameThread.isRunning():
                self.showGameBtn.setEnabled(False)
        else:
            self.showGame()

    def showGame(self):
        self.showingGame = True
        self.calendar.hide()
        self.gamesWidget.hide()
        self.text_widget.setPlainText("")
        self.text_widget.show()
        index = self.gamesWidget.row(self.gamesWidget.currentItem())
        gamePk = self.scheduleWorker.getGamePk(index)
        self.getPitches(gamePk)
        self.showGameBtn.setText("Return")

    def hideGame(self):
        self.stopLiveGameThread()
        self.showingGame = False
        self.calendar.show()
        self.text_widget.hide()
        self.text_widget.setPlainText(self.calendar.selectedDate().toString("MMMM d, yyyy"))
        self.gamesWidget.show()
        game = self.gamesWidget.currentItem()
        if game is not None and game.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
            self.showGameBtn.setText("View " + game.text() + " on " + self.calendar.selectedDate().toString("MMMM d, yyyy"))
        else:
            self.showGameBtn.setText("Select desired game...")

    def getPitches(self, gamePk):
        ##### Preset JSON file #####
        # with open("tests/meadows.json", "r") as f:
        #     game = json.load(f)

        ##### Assumes game is completed (no threading needed) #####
        # game = statsapi.get('game', {'gamePk': gamePk})
        # return pitchbypitch.listAllPitchesFromGame(game)

        ##### Print pitches for live game (threading required) #####
        self.startLiveGameThread(gamePk)

    def startLiveGameThread(self, gamePk):
        if self.liveGameThread is not None and self.liveGameThread.isRunning():
            self.stopLiveGameThread()
        self.liveGameThread = QtCore.QThread()
        self.liveGameWorker = LiveGameWorker(gamePk)
        self.liveGameWorker.moveToThread(self.liveGameThread)
        self.liveGameThread.started.connect(self.liveGameWorker.run)
        self.liveGameWorker.output.connect(self.updateGameOutput)
        self.liveGameWorker.finished.connect(self.liveGameThread.quit)
        self.liveGameWorker.finished.connect(self.liveGameWorker.deleteLater)
        self.liveGameThread.finished.connect(self.liveGameThread.deleteLater)
        self.liveGameThread.finished.connect(self.liveGameThreadFinished)
        self.liveGameThread.start()

    def startScheduleThread(self):
        if self.scheduleThread is not None and self.scheduleThread.isRunning():
            self.stopScheduleThread()
        self.scheduleThread = QtCore.QThread()
        self.scheduleWorker = schedule.ScheduleWorker()
        self.scheduleWorker.moveToThread(self.scheduleThread)
        self.scheduleThread.started.connect(self.scheduleWorker.run)
        self.scheduleWorker.output.connect(self.updateScheduleOutput)
        self.scheduleWorker.finished.connect(self.scheduleThread.quit)
        self.scheduleWorker.finished.connect(self.scheduleWorker.deleteLater)
        self.scheduleThread.finished.connect(self.scheduleThread.deleteLater)
        self.scheduleThread.finished.connect(self.scheduleThreadFinished)
        self.scheduleThread.start()

    def updateGameOutput(self, text):
        # update text_widget with text
        self.text_widget.append(text)
        
        # verbose print text to console
        vprint(text)

    def updateScheduleOutput(self):
        if not self.showingGame:
            self.text_widget.setPlainText(self.scheduleWorker.scheduleStr)
            self.text_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.gamesWidget.clear()
        self.gamesWidget.addItems(self.scheduleWorker.scheduleStr.split("\n"))

        header = self.gamesWidget.item(0)
        header.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
        label = QtWidgets.QLabel(header.text())
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        header.setText("")
        self.gamesWidget.setItemWidget(header, label)

    def stopAllThreads(self):
        self.stopLiveGameThread()
        self.stopScheduleThread()
        dprint("All threads stopped")

    def stopLiveGameThread(self):
        if self.liveGameThread is not None and self.liveGameThread.isRunning():
            dprint("Stopping live game worker")
            self.liveGameWorker.stop()
            dprint("Quitting live game thread")
            self.liveGameThread.quit()
            dprint("Waiting for live game thread")
            self.liveGameThread.wait()
            dprint("Live game thread stopped")

    def stopScheduleThread(self):
        if self.scheduleThread is not None and self.scheduleThread.isRunning():
            dprint("Stopping schedule worker")
            self.scheduleWorker.stop()
            dprint("Quitting schedule thread")
            self.scheduleThread.quit()
            dprint("Waiting for schedule thread")
            self.scheduleThread.wait()
            dprint("Schedule thread stopped")

    def liveGameThreadFinished(self):
        dprint("Live game thread finished")
        self.liveGameThread = None
        self.liveGameWorker = None
        self.showGameBtn.setEnabled(True)

    def scheduleThreadFinished(self):
        dprint("Schedule thread finished")
        self.scheduleThread = None
        self.scheduleWorker = None
    
    def initCalander(self):
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.show()
        self.calendar.selectionChanged.connect(self.updateDateSelected)
        self.updateDateSelected()
    
    def updateDateSelected(self):
        date = self.calendar.selectedDate()
        self.scheduleWorker.date = date
        self.scheduleWorker.update_event.set()

    def initGameSelected(self):
        self.gamesWidget = QtWidgets.QListWidget()
        self.gamesWidget.currentItemChanged.connect(self.updateGameSelected)
        self.updateGameSelected()

    def updateGameSelected(self):
        game = self.gamesWidget.currentItem()
        if game is not None and game.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
            self.showGameBtn.setText("View " + game.text() + " on " + self.calendar.selectedDate().toString("MMMM d, yyyy"))
            #print(game.text())

    def closeEvent(self, event):
        print("Application shutdown...")
        self.stopAllThreads()
        print("Done!")
        event.accept()

def main(args):
    cli.getOptions(args)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pitcher Painter")

    widget = ApplicationWidget()
    widget.resize(800, 600)
    #widget.resize(1000, 1000)
    widget.setWindowTitle("Pitcher Painter")
    widget.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main(sys.argv[1:])
