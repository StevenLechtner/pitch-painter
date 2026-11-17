"""Test the schedule.py methods"""


# pylint: disable=c-extension-no-member,no-name-in-module
from unittest.mock import patch
from PySide6 import QtCore
from pitchpainter.schedule import ScheduleWorker


@patch("pitchpainter.schedule.statsapi.schedule")
def test_grab_all_games_on_a_given_date(mock_schedule):
    """Test the result list of games played on September 5th, 2024 with a mocked statsapi.schedule API call response.

    This date had multiple baseball games played.
    """
    schedule = ScheduleWorker()
    date = QtCore.QDate()
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

    # Mock schedule response
    # pylint: disable=line-too-long
    mock_schedule.return_value = [{'game_id': 746664, 'game_datetime': '2024-09-05T17:10:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Houston Astros', 'home_name': 'Cincinnati Reds', 'away_id': 117, 'home_id': 113, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Rhett Lowder', 'away_probable_pitcher': 'Hunter Brown', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 0, 'home_score': 1, 'current_inning': 9, 'inning_state': 'Top', 'venue_id': 2602, 'venue_name': 'Great American Ball Park', 'national_broadcasts': ['MLBN (out-of-market only)'], 'series_status': 'CIN wins 3-0', 'winning_team': 'Cincinnati Reds', 'losing_team': 'Houston Astros', 'winning_pitcher': 'Tony Santillan', 'losing_pitcher': 'Bryan Abreu', 'save_pitcher': 'Alexis Díaz', 'summary': '2024-09-05 - Houston Astros (0) @ Cincinnati Reds (1) (Final)'}, {'game_id': 745042, 'game_datetime': '2024-09-05T17:10:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Minnesota Twins', 'home_name': 'Tampa Bay Rays', 'away_id': 142, 'home_id': 139, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Taj Bradley', 'away_probable_pitcher': 'Pablo López', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 4, 'home_score': 3, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 12, 'venue_name': 'Tropicana Field', 'national_broadcasts': ['MLBN (out-of-market only)'], 'series_status': 'Series tied 2-2', 'winning_team': 'Minnesota Twins', 'losing_team': 'Tampa Bay Rays', 'winning_pitcher': 'Pablo López', 'losing_pitcher': 'Taj Bradley', 'save_pitcher': 'Jhoan Duran', 'summary': '2024-09-05 - Minnesota Twins (4) @ Tampa Bay Rays (3) (Final)'}, {'game_id': 745612, 'game_datetime': '2024-09-05T19:37:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Seattle Mariners', 'home_name': 'Oakland Athletics', 'away_id': 136, 'home_id': 133, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Joey Estes', 'away_probable_pitcher': 'Bryan Woo', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 6, 'home_score': 4, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 10, 'venue_name': 'Oakland Coliseum', 'national_broadcasts': [], 'series_status': 'Series tied 2-2', 'winning_team': 'Seattle Mariners', 'losing_team': 'Oakland Athletics', 'winning_pitcher': 'Bryan Woo', 'losing_pitcher': 'Joey Estes', 'save_pitcher': None, 'summary': '2024-09-05 - Seattle Mariners (6) @ Oakland Athletics (4) (Final)'}, {'game_id': 745289, 'game_datetime': '2024-09-05T19:45:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Arizona Diamondbacks', 'home_name': 'San Francisco Giants', 'away_id': 109, 'home_id': 137, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Blake Snell', 'away_probable_pitcher': 'Merrill Kelly', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 2, 'home_score': 3, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 2395, 'venue_name': 'Oracle Park', 'national_broadcasts': [], 'series_status': 'AZ wins 2-1', 'winning_team': 'San Francisco Giants', 'losing_team': 'Arizona Diamondbacks', 'winning_pitcher': 'Ryan Walker', 'losing_pitcher': 'Kevin Ginkel', 'save_pitcher': None, 'summary': '2024-09-05 - Arizona Diamondbacks (2) @ San Francisco Giants (3) (Final)'}, {'game_id': 745451, 'game_datetime': '2024-09-05T22:40:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Washington Nationals', 'home_name': 'Pittsburgh Pirates', 'away_id': 120, 'home_id': 134, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Bailey Falter', 'away_probable_pitcher': 'Jake Irvin', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 4, 'home_score': 9, 'current_inning': 9, 'inning_state': 'Top', 'venue_id': 31, 'venue_name': 'PNC Park', 'national_broadcasts': ['MLBN (out-of-market only)'], 'series_status': 'PIT leads 1-0', 'winning_team': 'Pittsburgh Pirates', 'losing_team': 'Washington Nationals', 'winning_pitcher': 'Bailey Falter', 'losing_pitcher': 'Jake Irvin', 'save_pitcher': 'Aroldis Chapman', 'summary': '2024-09-05 - Washington Nationals (4) @ Pittsburgh Pirates (9) (Final)'}, {'game_id': 746021, 'game_datetime': '2024-09-05T22:40:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Philadelphia Phillies', 'home_name': 'Miami Marlins', 'away_id': 143, 'home_id': 146, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Adam Oller', 'away_probable_pitcher': 'Ranger Suarez', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 5, 'home_score': 2, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 4169, 'venue_name': 'loanDepot park', 'national_broadcasts': ['MLBN (out-of-market only)'], 'series_status': 'PHI leads 1-0', 'winning_team': 'Philadelphia Phillies', 'losing_team': 'Miami Marlins', 'winning_pitcher': 'Ranger Suarez', 'losing_pitcher': 'Adam Oller', 'save_pitcher': 'Matt Strahm', 'summary': '2024-09-05 - Philadelphia Phillies (5) @ Miami Marlins (2) (Final)'}, {'game_id': 747073, 'game_datetime': '2024-09-05T23:20:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Colorado Rockies', 'home_name': 'Atlanta Braves', 'away_id': 115, 'home_id': 144, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Reynaldo López', 'away_probable_pitcher': 'Austin Gomber', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 3, 'home_score': 1, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 4705, 'venue_name': 'Truist Park', 'national_broadcasts': ['MLB.tv Free Game'], 'series_status': 'ATL wins 2-1', 'winning_team': 'Colorado Rockies', 'losing_team': 'Atlanta Braves', 'winning_pitcher': 'Austin Gomber', 'losing_pitcher': 'Reynaldo López', 'save_pitcher': 'Tyler Kinley', 'summary': '2024-09-05 - Colorado Rockies (3) @ Atlanta Braves (1) (Final)'}, {'game_id': 744966, 'game_datetime': '2024-09-06T00:05:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Los Angeles Angels', 'home_name': 'Texas Rangers', 'away_id': 108, 'home_id': 140, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Cody Bradford', 'away_probable_pitcher': 'Jack Kochanowicz', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 1, 'home_score': 3, 'current_inning': 9, 'inning_state': 'Top', 'venue_id': 5325, 'venue_name': 'Globe Life Field', 'national_broadcasts': [], 'series_status': 'TEX leads 1-0', 'winning_team': 'Texas Rangers', 'losing_team': 'Los Angeles Angels', 'winning_pitcher': 'Cody Bradford', 'losing_pitcher': 'Jack Kochanowicz', 'save_pitcher': 'Kirby Yates', 'summary': '2024-09-05 - Los Angeles Angels (1) @ Texas Rangers (3) (Final)'}, {'game_id': 745369, 'game_datetime': '2024-09-06T00:40:00Z', 'game_date': '2024-09-05', 'game_type': 'R', 'status': 'Final', 'away_name': 'Detroit Tigers', 'home_name': 'San Diego Padres', 'away_id': 116, 'home_id': 135, 'doubleheader': 'N', 'game_num': 1, 'home_probable_pitcher': 'Martín Pérez', 'away_probable_pitcher': 'Casey Mize', 'home_pitcher_note': '', 'away_pitcher_note': '', 'away_score': 4, 'home_score': 3, 'current_inning': 9, 'inning_state': 'Bottom', 'venue_id': 2680, 'venue_name': 'Petco Park', 'national_broadcasts': [], 'series_status': 'SD wins 2-1', 'winning_team': 'Detroit Tigers', 'losing_team': 'San Diego Padres', 'winning_pitcher': 'Ricky Vanasco', 'losing_pitcher': 'Robert Suarez', 'save_pitcher': 'Tyler Holton', 'summary': '2024-09-05 - Detroit Tigers (4) @ San Diego Padres (3) (Final)'}]  # noqa

    date.setDate(2024, 9, 5)
    schedule.set_date(date)
    schedule.set_schedule_str()
    assert schedule.schedule_str == correct_output


@patch("pitchpainter.schedule.statsapi.schedule")
def test_no_games_on_a_given_date(mock_schedule):
    """Test the result list of games played on December 25th, 2025 with a mocked statsapi.schedule API call response.

    This date had no baseball games played.
    """
    schedule = ScheduleWorker()
    date = QtCore.QDate()
    correct_output = "No games played on December 25, 2025"

    # Mock schedule response
    mock_schedule.return_value = []

    date.setDate(2025, 12, 25)
    schedule.set_date(date)
    schedule.set_schedule_str()
    assert schedule.schedule_str == correct_output
