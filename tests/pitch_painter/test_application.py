from pitchpainter.application import ApplicationWidget
from pytestqt.qtbot import QtBot

def test_init(qtbot: QtBot):
    widget = ApplicationWidget()
    qtbot.addWidget(widget)
    widget.showGameBtn.click()
    assert widget.showingGame == True
