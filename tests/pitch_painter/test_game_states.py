"""Test various game over and start scenarios."""


from pitchpainter.game import Game, Status
from pitchpainter.game_processor import GameProcessor


def test_delayed_start():
    """Test a game delay shows the game is not LIVE."""
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/delayed_start.json")
    game.set_status()
    assert game.game_status == Status.PREVIEW


def test_extra_inning_final():
    """Test both away team and home team winning in extra innings shows game over."""
    # away team wins in extras
    away_win_game = Game()
    away_win_game.get_game_by_file_path("tests/pitch_painter/data/extra_innings_away_wins.json")
    away_win_game.situation.set_inning(away_win_game.at_bats[-2].get("about", {}).get("inning", -1))
    away_win_game.situation.set_top(away_win_game.at_bats[-2].get("about", {}).get("isTopInning", False))
    away_win_game.process_at_bat_finished(away_win_game.at_bats[-2])
    assert away_win_game.game_over is False
    away_win_game.situation.set_inning(away_win_game.at_bats[-1].get("about", {}).get("inning", -1))
    away_win_game.situation.set_top(away_win_game.at_bats[-1].get("about", {}).get("isTopInning", False))
    away_win_game.process_at_bat_finished(away_win_game.at_bats[-1])
    assert away_win_game.game_over is True

    # TODO: test home team extra inning walk off


def test_no_extra_inning_final():
    """Test both away team and home team winning in 9 innings shows game over."""
    # TODO: test away team wins no extras
    # away_win_game = Game()

    # home team wins in a 9th inning walk off
    walk_off = Game()
    walk_off.get_game_by_file_path("tests/pitch_painter/data/example_game_end.json")
    walk_off.situation.set_inning(walk_off.at_bats[-2].get("about", {}).get("inning", -1))
    walk_off.situation.set_top(walk_off.at_bats[-2].get("about", {}).get("isTopInning", False))
    walk_off.process_at_bat_finished(walk_off.at_bats[-2])
    assert walk_off.game_over is False
    walk_off.situation.set_inning(walk_off.at_bats[-1].get("about", {}).get("inning", -1))
    walk_off.situation.set_top(walk_off.at_bats[-1].get("about", {}).get("isTopInning", False))
    walk_off.process_at_bat_finished(walk_off.at_bats[-1])
    assert walk_off.game_over is True

    # TODO: home team wins with no walk off, no extras


def test_pitching_change_mid_at_bat():
    """Test pitcher and pitch count update on pitching change during an at bat, but no count or baserunner change."""
    processor = GameProcessor(filepath="tests/pitch_painter/data/pitching_change_mid_at_bat.json")
    # Anthony Banda replaces Shohei Ohtani
    # at bat 30, 0=ball, 1=ball, 2=injury, 3=pitch_change, 4=defensive_switch, 5=ball
    processor.process_at_bat(29)
    assert processor.game.situation.pitcher == "Shohei Ohtani"
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[0],
                                 processor.game.at_bats[30])  # ball
    assert processor.game.situation.pitcher == "Shohei Ohtani"
    assert processor.game.situation.pitch_count == 5
    assert processor.game.situation.balls == 1
    assert processor.game.situation.strikes == 0
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[1],
                                 processor.game.at_bats[30])  # ball
    assert processor.game.situation.pitcher == "Shohei Ohtani"
    assert processor.game.situation.pitch_count == 6
    assert processor.game.situation.balls == 2
    assert processor.game.situation.strikes == 0
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[2],
                                 processor.game.at_bats[30])  # injury
    assert processor.game.situation.pitcher == "Shohei Ohtani"
    assert processor.game.situation.pitch_count == 6
    assert processor.game.situation.balls == 2
    assert processor.game.situation.strikes == 0
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[3],
                                 processor.game.at_bats[30])  # pitching change
    assert processor.game.situation.pitcher == "Anthony Banda"
    assert processor.game.situation.pitch_count == 0
    assert processor.game.situation.balls == 2
    assert processor.game.situation.strikes == 0
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[4],
                                 processor.game.at_bats[30])  # defensive substitution
    assert processor.game.situation.pitcher == "Anthony Banda"
    assert processor.game.situation.pitch_count == 0
    assert processor.game.situation.balls == 2
    assert processor.game.situation.strikes == 0
    processor.process_play_event(processor.game.at_bats[30].get("playEvents", [])[5],
                                 processor.game.at_bats[30])  # ball
    assert processor.game.situation.pitcher == "Anthony Banda"
    assert processor.game.situation.pitch_count == 1
    assert processor.game.situation.balls == 3
    assert processor.game.situation.strikes == 0


def test_live_pitching_change():
    """Test pitcher and pitch count update on pitching change during a live game."""
    processor = GameProcessor(filepath="tests/pitch_painter/data/live_pitching_change_mid_inning.json")
    # 0=mound_visit, 1=pitching_change
    processor.process_at_bat(64)
    # init pitcher manually for testing
    processor.game.situation.set_pitcher("Ben Joyce")
    processor.game.pitcher_info.cur_home_pitcher = "Ben Joyce"
    assert processor.game.situation.pitcher == "Ben Joyce"
    assert processor.game.situation.outs == 2
    processor.process_play_event(processor.game.at_bats[-1].get("playEvents", [])[0],
                                 processor.game.at_bats[-1])  # mound visit
    assert processor.game.situation.pitcher == "Ben Joyce"
    assert processor.game.situation.outs == 2
    processor.process_play_event(processor.game.at_bats[-1].get("playEvents", [])[1],
                                 processor.game.at_bats[-1])  # pitching change
    assert processor.game.situation.pitcher == "Sammy Peralta"
    assert processor.game.situation.pitch_count == 0
    assert processor.game.situation.balls == 0
    assert processor.game.situation.strikes == 0
    assert processor.game.situation.outs == 2
