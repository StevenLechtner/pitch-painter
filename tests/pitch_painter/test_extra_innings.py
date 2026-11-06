from pitchpainter.game import Game


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
