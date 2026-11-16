from pitchpainter.game import Game
#from pitchpainter.live_game import process_play_event, process_at_bat
from pitchpainter.game_processor import GameProcessor


def test_ghost_runner():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/ghost_runner_worked_somehow.json")
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    game.situation.set_baserunners_at_start_of_at_bat(game.at_bats[86])  # top of the 10th ghost runner put on
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == False
    game.situation.set_baserunners_at_end_of_at_bat(game.at_bats[86])  # single leads to first and third
    assert game.situation.baserunners[1] == True
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == True

def test_ghost_runner_live():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/ghost_runner_added_live.json")
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    game.situation.set_baserunners_at_start_of_at_bat(game.at_bats[-1])  # live game top of the 10th start
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == False

def test_wild_pitch():
    processor = GameProcessor(filepath="tests/pitch_painter/data/wild_pitch.json")
    processor.game.process_at_bat_finished(processor.game.at_bats[52])
    processor.process_play_event(processor.game.at_bats[53].get("playEvents", [])[3],
                                 processor.game.at_bats[53])  # runners on second and third before the wild pitch
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == True
    assert processor.game.situation.baserunners[3] == True
    assert processor.game.situation.away_score == 6
    processor.process_play_event(processor.game.at_bats[53].get("playEvents", [])[4],
                                 processor.game.at_bats[53])  # wild pitch leads to runner on third + score
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == True
    assert processor.game.situation.away_score == 7

    liveGame = GameProcessor(filepath="tests/pitch_painter/data/live_wild_pitch.json")
    liveGame.game.process_at_bat_finished(liveGame.game.at_bats[7])
    liveGame.process_play_event(liveGame.game.at_bats[-1].get("playEvents", [])[-2],
                                liveGame.game.at_bats[-1])  # live game runners on first and third before the wild pitch
    assert liveGame.game.situation.baserunners[1] == True
    assert liveGame.game.situation.baserunners[2] == True
    assert liveGame.game.situation.baserunners[3] == False
    liveGame.process_play_event(liveGame.game.at_bats[-1].get("playEvents", [])[-1],
                                liveGame.game.at_bats[-1])  # live game's last pitch wild moved second to third, first stays
    assert liveGame.game.situation.baserunners[1] == True
    assert liveGame.game.situation.baserunners[2] == False
    assert liveGame.game.situation.baserunners[3] == True

    # TODO: write test for live_wild_pitch_double_steal as well

def test_stolen_every_base_same_at_bat():
    processor = GameProcessor(filepath="tests/pitch_painter/data/steal_second_third_and_home.json")
    processor.process_at_bat(58)
    assert processor.game.situation.baserunners[1] == True
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[1],
                                 processor.game.at_bats[59])  # normal ball
    assert processor.game.situation.baserunners[1] == True
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[2],
                                 processor.game.at_bats[59])  # Elly steals second
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == True
    assert processor.game.situation.baserunners[3] == False
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[5],
                                 processor.game.at_bats[59])  # Elly steals third
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == True
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[6],
                                 processor.game.at_bats[59])  # no_pitch
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == True
    assert processor.game.situation.away_score == 6
    processor.process_play_event(processor.game.at_bats[59].get("playEvents", [])[7],
                                 processor.game.at_bats[59]) # Elly steals home (same pitch as stealing third)
    assert processor.game.situation.baserunners[1] == False
    assert processor.game.situation.baserunners[2] == False
    assert processor.game.situation.baserunners[3] == False
    assert processor.game.situation.away_score == 7
