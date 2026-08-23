import statsapi
import json
import pitchbypitch
import application_util
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
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
        else:
            self.showGame()

    def showGame(self):
        self.showingGame = True
        self.calendar.hide()
        self.gamesWidget.hide()
        self.text_widget.show()
        index = self.gamesWidget.row(self.gamesWidget.currentItem())
        gamePk = application_util.getGamePk(index)
        self.text_widget.setPlainText("\n".join(self.getPitches(gamePk)))
        self.showGameBtn.setText("Return")

    def hideGame(self):
        self.showingGame = False
        self.calendar.show()
        self.text_widget.hide()
        self.text_widget.setPlainText(self.calendar.selectedDate().toString("MMMM d, yyyy"))
        self.gamesWidget.show()
        self.showGameBtn.setText("Select desired game...")

    def getPitches(self, gamePk):
        # with open("meadows.json", "r") as f:
        #     game = json.load(f)
        game = statsapi.get('game', {'gamePk': gamePk})
        return pitchbypitch.listAllPitchesFromGame(game)
    
    def initCalander(self):
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.show()
        self.calendar.selectionChanged.connect(self.updateDateSelected)
        self.updateDateSelected()
    
    def updateDateSelected(self):
        date = self.calendar.selectedDate()
        year = date.year()
        month = date.month()
        day = date.day()
        #self.text_widget.setPlainText(date.toString("MMMM d, yyyy"))
        scheduleStr = application_util.getScheduleStr(date)
        scheduleList = scheduleStr.split("\n")
        self.text_widget.setPlainText(scheduleStr)
        self.gamesWidget.clear()
        self.gamesWidget.addItems(scheduleList)

        header = self.gamesWidget.item(0)
        header.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
        label = QtWidgets.QLabel(header.text())
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        header.setText("")
        self.gamesWidget.setItemWidget(header, label)

        self.text_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def initGameSelected(self):
        self.gamesWidget = QtWidgets.QListWidget()
        self.gamesWidget.currentItemChanged.connect(self.updateGameSelected)
        self.updateGameSelected()

    def updateGameSelected(self):
        game = self.gamesWidget.currentItem()
        if game is not None and game.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
            self.showGameBtn.setText("View " + game.text() + " on " + self.calendar.selectedDate().toString("MMMM d, yyyy"))
            print(game.text())

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pitcher Painter")

    widget = MyWidget()
    #widget.resize(800, 600)
    widget.resize(1000, 1000)
    widget.setWindowTitle("Pitcher Painter")
    widget.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
