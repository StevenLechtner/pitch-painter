from pitchpainter.application import ApplicationWidget
from pytestqt.qtbot import QtBot
from PySide6 import QtCore

def test_init(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.showingGame == False
    widget.closeEvent(None)

def test_choose_date(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.showGameBtn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.gamesWidget.count() > 1, timeout=5000)
    assert widget.gamesWidget.count() == 10
    item = widget.gamesWidget.item(widget.gamesWidget.count() - 1)
    widget.gamesWidget.setCurrentItem(item)
    assert widget.showGameBtn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.closeEvent(None)

def test_start_game(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.showGameBtn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.gamesWidget.count() > 1, timeout=5000)
    assert widget.gamesWidget.count() == 10
    item = widget.gamesWidget.item(widget.gamesWidget.count() - 1)
    widget.gamesWidget.setCurrentItem(item)
    assert widget.showGameBtn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.showGameBtn.click()
    assert widget.showingGame == True
    widget.closeEvent(None)

def test_return_from_game(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.showGameBtn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.gamesWidget.count() > 1, timeout=5000)
    assert widget.gamesWidget.count() == 10
    item = widget.gamesWidget.item(widget.gamesWidget.count() - 1)
    widget.gamesWidget.setCurrentItem(item)
    assert widget.showGameBtn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.showGameBtn.click()
    assert widget.showingGame == True
    assert widget.showGameBtn.text() == "Return"
    widget.showGameBtn.click()
    assert widget.showingGame == False
    assert widget.showGameBtn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.closeEvent(None)
