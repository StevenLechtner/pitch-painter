from pitchpainter.application import ApplicationWidget
from pytestqt.qtbot import QtBot
from PySide6 import QtCore

def test_init(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.showing_game == False
    widget.closeEvent(None)

def test_choose_date(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.show_game_btn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.games_widget.count() > 1, timeout=5000)
    assert widget.games_widget.count() == 10
    item = widget.games_widget.item(widget.games_widget.count() - 1)
    widget.games_widget.setCurrentItem(item)
    assert widget.show_game_btn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.closeEvent(None)

def test_start_game(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.show_game_btn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.games_widget.count() > 1, timeout=5000)
    assert widget.games_widget.count() == 10
    item = widget.games_widget.item(widget.games_widget.count() - 1)
    widget.games_widget.setCurrentItem(item)
    assert widget.show_game_btn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.show_game_btn.click()
    assert widget.showing_game == True
    widget.closeEvent(None)

def test_return_from_game(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    assert widget.show_game_btn.text() == "Select desired game..."
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    widget.calendar.setSelectedDate(date)
    qtbot.waitUntil(lambda: widget.games_widget.count() > 1, timeout=5000)
    assert widget.games_widget.count() == 10
    item = widget.games_widget.item(widget.games_widget.count() - 1)
    widget.games_widget.setCurrentItem(item)
    assert widget.show_game_btn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.show_game_btn.click()
    assert widget.showing_game == True
    assert widget.show_game_btn.text() == "Return"
    widget.show_game_btn.click()
    assert widget.showing_game == False
    assert widget.show_game_btn.text() == "View Detroit Tigers (4) @ San Diego Padres (3) (Final) on September 5, 2024"
    widget.closeEvent(None)
