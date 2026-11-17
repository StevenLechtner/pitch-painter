"""Test automatic ball and strike (ABS) challenge calls."""


from pitchpainter.game import Game
from pitchpainter.game_processor import GameProcessor


def test_inning_ending_k_to_bb():
    """Test a full count two out original call strike (end inning) overturned to ball (continue inning + walk)."""
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/abs_challenge_overturned_from_k_to_bb_with_two_outs.json")
    game.process_at_bat_finished(game.at_bats[58])
    assert game.situation.baserunners[1] is True
    assert game.situation.baserunners[2] is True
    assert game.situation.baserunners[3] is True
    assert game.situation.outs == 2


def test_pitch_clock_violation():
    """Test a pitch clock violation resulting in a 'ball' with no pitch count increase."""
    # first pitch normal ball (1-0)
    processor = GameProcessor(filepath="tests/pitch_painter/data/pitch_clock_violation.json")
    processor.process_play_event(processor.game.at_bats[-1].get("playEvents", [])[0], processor.game.at_bats[-1])
    assert processor.game.situation.balls == 1
    assert processor.game.situation.strikes == 0
    assert processor.game.situation.pitch_count == 1
    # pitcher violation (2-0), pitch count does not increment
    processor.process_play_event(processor.game.at_bats[-1].get("playEvents", [])[1], processor.game.at_bats[-1])
    assert processor.game.situation.balls == 2
    assert processor.game.situation.strikes == 0
    assert processor.game.situation.pitch_count == 1
    # third pitch normal ball (3-0), but pitch count is still at 2
    processor.process_play_event(processor.game.at_bats[-1].get("playEvents", [])[2], processor.game.at_bats[-1])
    assert processor.game.situation.balls == 3
    assert processor.game.situation.strikes == 0
    assert processor.game.situation.pitch_count == 2
