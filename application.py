import json
import pitchbypitch
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.showingGame = False
        self.showGameBtn = QtWidgets.QPushButton("Click Me!")

        self.text_widget = QtWidgets.QTextEdit()
        font = QtGui.QFont("Menlo", 12)
        font.setFixedPitch(True)
        self.text_widget.setFont(font)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        self.calendar = self.getDate()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.calendar)
        self.layout.addWidget(self.text_widget)
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
        self.text_widget.setPlainText("\n".join(self.getPitches()))
        self.showGameBtn.setText("Return")

    def hideGame(self):
        self.showingGame = False
        self.calendar.show()
        self.text_widget.setPlainText(self.calendar.selectedDate().toString("MMMM d, yyyy"))
        self.showGameBtn.setText("Click Me!")

    def getPitches(self):
        with open("meadows.json", "r") as f:
            game = json.load(f)
        return pitchbypitch.listAllPitchesFromGame(game)
    
    def getDate(self):
        calendar = QtWidgets.QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.show()

        self.text_widget.setPlainText(calendar.selectedDate().toString("MMMM d, yyyy"))
        self.text_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        calendar.selectionChanged.connect(self.update_date_text)

        return calendar
    
    def update_date_text(self):
        self.text_widget.setPlainText(self.calendar.selectedDate().toString("MMMM d, yyyy"))
        self.text_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pitcher Painter")

    widget = MyWidget()
    widget.resize(800, 600)
    widget.setWindowTitle("Pitcher Painter")
    widget.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
