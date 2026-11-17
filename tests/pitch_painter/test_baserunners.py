"""Test the Situation object's baserunners are correct after whacky events."""


from pitchpainter.game import Game
from pitchpainter.game_processor import GameProcessor


def test_ghost_runner():
    """Test a runner automatically starts on second base in extra innings."""
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/ghost_runner_worked_somehow.json")
    assert game.situation.baserunners[1] is False
    assert game.situation.baserunners[2] is False
    assert game.situation.baserunners[3] is False
    game.situation.set_baserunners_at_start_of_at_bat(game.at_bats[86])  # top of the 10th ghost runner put on
    assert game.situation.baserunners[1] is False
    assert game.situation.baserunners[2] is True
    assert game.situation.baserunners[3] is False
    game.situation.set_baserunners_at_end_of_at_bat(game.at_bats[86])  # single leads to first and third
    assert game.situation.baserunners[1] is True
    assert game.situation.baserunners[2] is False
    assert game.situation.baserunners[3] is True


def test_ghost_runner_live():
    """Test a runner automatically starts on second base in extra innings with a live game output."""
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/ghost_runner_added_live.json")
    assert game.situation.baserunners[1] is False
    assert game.situation.baserunners[2] is False
    assert game.situation.baserunners[3] is False
    game.situation.set_baserunners_at_start_of_at_bat(game.at_bats[-1])  # live game top of the 10th start
    assert game.situation.baserunners[1] is False
    assert game.situation.baserunners[2] is True
    assert game.situation.baserunners[3] is False


def test_wild_pitch():
    """Test that a wild pitch with runners advancing does indicate the runners advances."""
    processor = GameProcessor(filepath="tests/pitch_painter/data/wild_pitch.json")
    processor.game.process_at_bat_finished(processor.game.at_bats[52])
    processor.process_play_event(processor.game.at_bats[53].get("playEvents", [])[3],
                                 processor.game.at_bats[53])  # runners on second and third before the wild pitch
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is True
    assert processor.game.situation.baserunners[3] is True
    assert processor.game.situation.away_score == 6
    processor.process_play_event(processor.game.at_bats[53].get("playEvents", [])[4],
                                 processor.game.at_bats[53])  # wild pitch leads to runner on third + score
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is True
    assert processor.game.situation.away_score == 7

    live_game = GameProcessor(filepath="tests/pitch_painter/data/live_wild_pitch.json")
    live_game.game.process_at_bat_finished(live_game.game.at_bats[7])
    live_game.process_play_event(live_game.game.at_bats[-1].get("playEvents", [])[-2],
                                 live_game.game.at_bats[-1])  # live game runners on first and third before wild pitch
    assert live_game.game.situation.baserunners[1] is True
    assert live_game.game.situation.baserunners[2] is True
    assert live_game.game.situation.baserunners[3] is False
    live_game.process_play_event(live_game.game.at_bats[-1].get("playEvents", [])[-1],
                                 live_game.game.at_bats[-1])  # wild pitch moved second to third, first stays
    assert live_game.game.situation.baserunners[1] is True
    assert live_game.game.situation.baserunners[2] is False
    assert live_game.game.situation.baserunners[3] is True

    # TODO: write test for live_wild_pitch_double_steal as well


def test_stolen_every_base_same_at_bat():
    """Test correct output of Elly De La Cruz stealing second, third, and home all in the same at bat."""
    processor = GameProcessor(filepath="tests/pitch_painter/data/steal_second_third_and_home.json")
    processor.process_at_bat(58)
    assert processor.game.situation.baserunners[1] is True
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[1],
                                 processor.game.at_bats[59])  # normal ball
    assert processor.game.situation.baserunners[1] is True
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[2],
                                 processor.game.at_bats[59])  # Elly steals second
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is True
    assert processor.game.situation.baserunners[3] is False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[5],
                                 processor.game.at_bats[59])  # Elly steals third
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is True
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[6],
                                 processor.game.at_bats[59])  # no_pitch
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is True
    assert processor.game.situation.away_score == 6
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[7],
                                 processor.game.at_bats[59])  # Elly steals home (same pitch as stealing third)
    assert processor.game.situation.baserunners[1] is False
    assert processor.game.situation.baserunners[2] is False
    assert processor.game.situation.baserunners[3] is False
    assert processor.game.situation.away_score == 7
