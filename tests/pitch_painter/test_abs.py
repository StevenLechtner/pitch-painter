from pitchpainter.game import Game
from pitchpainter.live_game import process_play_event


def test_inning_ending_k_to_bb():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/abs_challenge_overturned_from_k_to_bb_with_two_outs.json")
    game.process_at_bat_finished(game.at_bats[58])
    assert game.situation.baserunners[1] == True
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == True
    assert game.situation.outs == 2

def test_pitch_clock_violation():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/pitch_clock_violation.json")
    # first pitch normal ball (1-0)
    process_play_event(game.at_bats[-1].get("playEvents", [])[0], game.situation, game.at_bats[-1], game, None)
    assert game.situation.balls == 1
    assert game.situation.strikes == 0
    assert game.situation.pitch_count == 1
    # pitcher violation (2-0), pitch count does not increment
    process_play_event(game.at_bats[-1].get("playEvents", [])[1], game.situation, game.at_bats[-1], game, None)
    assert game.situation.balls == 2
    assert game.situation.strikes == 0
    assert game.situation.pitch_count == 1
    # third pitch normal ball (3-0), but pitch count is still at 2
    process_play_event(game.at_bats[-1].get("playEvents", [])[2], game.situation, game.at_bats[-1], game, None)
    assert game.situation.balls == 3
    assert game.situation.strikes == 0
    assert game.situation.pitch_count == 2