from pitchpainter.game import Game
from pitchpainter.live_game import processPlayEvent, processAtBat


def test_ghost_runner():
    game = Game()
    game.getGameByFilePath("tests/pitch_painter/data/ghost_runner_worked_somehow.json")
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    game.situation.setBaserunnersAtStartOfAtBat(game.atBats[86])  # top of the 10th ghost runner put on
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == False
    game.situation.setBaserunnersAtEndOfAtBat(game.atBats[86])  # single leads to first and third
    assert game.situation.baserunners[1] == True
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == True

def test_ghost_runner_live():
    game = Game()
    game.getGameByFilePath("tests/pitch_painter/data/ghost_runner_added_live.json")
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    game.situation.setBaserunnersAtStartOfAtBat(game.atBats[-1])  # live game top of the 10th start
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == False

def test_wild_pitch():
    game = Game()
    game.getGameByFilePath("tests/pitch_painter/data/wild_pitch.json")
    game.processAtBatFinished(game.atBats[52])  # set situation to the wild pitch at bat
    processPlayEvent(game.atBats[53].get("playEvents", [])[3],
                     game.situation,
                     game.atBats[53],
                     game,
                     None)  # runners on second and third before the wild pitch
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == True
    assert game.situation.awayScore == 6
    processPlayEvent(game.atBats[53].get("playEvents", [])[4],
                     game.situation,
                     game.atBats[53],
                     game,
                     None)  # wild pitch leads to runner on third + score
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == True
    assert game.situation.awayScore == 7

    liveGame = Game()
    liveGame.getGameByFilePath("tests/pitch_painter/data/live_wild_pitch.json")
    liveGame.processAtBatFinished(liveGame.atBats[7])
    processPlayEvent(liveGame.atBats[-1].get("playEvents", [])[-2],
                     liveGame.situation,
                     liveGame.atBats[-1],
                     liveGame,
                     None)  # live game runners on first and third before the wild pitch
    assert liveGame.situation.baserunners[1] == True
    assert liveGame.situation.baserunners[2] == True
    assert liveGame.situation.baserunners[3] == False
    processPlayEvent(liveGame.atBats[-1].get("playEvents", [])[-1],
                     liveGame.situation,
                     liveGame.atBats[-1],
                     liveGame,
                     None)  # live game's last pitch wild moved second to third, first stays
    assert liveGame.situation.baserunners[1] == True
    assert liveGame.situation.baserunners[2] == False
    assert liveGame.situation.baserunners[3] == True

    # TODO: write test for live_wild_pitch_double_steal as well

def test_stolen_every_base_same_at_bat():
    game = Game()
    game.getGameByFilePath("tests/pitch_painter/data/steal_second_third_and_home.json")
    processAtBat(game, 58, None, None, None)
    assert game.situation.baserunners[1] == True
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    processPlayEvent(game.atBats[59].get("playEvents", [])[1],
                     game.situation,
                     game.atBats[59],
                     game,
                     None)  # normal ball
    assert game.situation.baserunners[1] == True
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    processPlayEvent(game.atBats[59].get("playEvents", [])[2],
                     game.situation,
                     game.atBats[59],
                     game,
                     None)  # Elly steals second
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == True
    assert game.situation.baserunners[3] == False
    processPlayEvent(game.atBats[59].get("playEvents", [])[5],
                     game.situation,
                     game.atBats[59],
                     game,
                     None)  # Elly steals third
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == True
    processPlayEvent(game.atBats[59].get("playEvents", [])[6],
                     game.situation,
                     game.atBats[59],
                     game,
                     None)  # no_pitch
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == True
    assert game.situation.awayScore == 6
    processPlayEvent(game.atBats[59].get("playEvents", [])[7],
                     game.situation,
                     game.atBats[59],
                     game,
                     None)  # Elly steals home (same pitch as stealing third)
    assert game.situation.baserunners[1] == False
    assert game.situation.baserunners[2] == False
    assert game.situation.baserunners[3] == False
    assert game.situation.awayScore == 7