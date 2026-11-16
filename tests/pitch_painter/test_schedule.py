from PySide6 import QtCore
from pitchpainter.schedule import ScheduleWorker


def test_grab_all_games_on_a_given_date():
    schedule = ScheduleWorker()
    date = QtCore.QDate()
    date.setDate(2024, 9, 5)
    schedule.set_date(date)
    schedule.set_schedule_str()
    correct_output = (
        "Games for September 5, 2024:\n"
        "Houston Astros (0) @ Cincinnati Reds (1) (Final)\n"
        "Minnesota Twins (4) @ Tampa Bay Rays (3) (Final)\n"
        "Seattle Mariners (6) @ Oakland Athletics (4) (Final)\n"
        "Arizona Diamondbacks (2) @ San Francisco Giants (3) (Final)\n"
        "Washington Nationals (4) @ Pittsburgh Pirates (9) (Final)\n"
        "Philadelphia Phillies (5) @ Miami Marlins (2) (Final)\n"
        "Colorado Rockies (3) @ Atlanta Braves (1) (Final)\n"
        "Los Angeles Angels (1) @ Texas Rangers (3) (Final)\n"
        "Detroit Tigers (4) @ San Diego Padres (3) (Final)"
    )
    assert schedule.schedule_str == correct_output


def test_no_games_on_a_given_date():
    schedule = ScheduleWorker()
    date = QtCore.QDate()
    date.setDate(2025, 12, 25)
    schedule.set_date(date)
    schedule.set_schedule_str()
    correct_output = ("No games played on December 25, 2025")
    assert schedule.schedule_str == correct_output
