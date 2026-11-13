from pitchpainter.game import Game, Status
from pitchpainter.live_game import process_play_event, process_at_bat


def test_delayed_start():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/delayed_start.json")
    game.set_status()
    assert game.game_status == Status.PREVIEW

def test_extra_inning_final():
    # away team wins in extras
    awayWinGame = Game()
    awayWinGame.get_game_by_file_path("tests/pitch_painter/data/extra_innings_away_wins.json")
    awayWinGame.situation.setInning(awayWinGame.at_bats[-2].get("about", {}).get("inning", -1))
    awayWinGame.situation.setTop(awayWinGame.at_bats[-2].get("about", {}).get("isTopInning", False))
    awayWinGame.process_at_bat_finished(awayWinGame.at_bats[-2])
    assert awayWinGame.game_over == False
    awayWinGame.situation.setInning(awayWinGame.at_bats[-1].get("about", {}).get("inning", -1))
    awayWinGame.situation.setTop(awayWinGame.at_bats[-1].get("about", {}).get("isTopInning", False))
    awayWinGame.process_at_bat_finished(awayWinGame.at_bats[-1])
    assert awayWinGame.game_over == True

    # TODO: test home team extra inning walk off

def test_no_extra_inning_final():
    # TODO: test away team wins no extras
    awayWinGame = Game()

    # home team wins in a 9th inning walk off
    walkOff = Game()
    walkOff.get_game_by_file_path("tests/pitch_painter/data/example_game_end.json")
    walkOff.situation.setInning(walkOff.at_bats[-2].get("about", {}).get("inning", -1))
    walkOff.situation.setTop(walkOff.at_bats[-2].get("about", {}).get("isTopInning", False))
    walkOff.process_at_bat_finished(walkOff.at_bats[-2])
    assert walkOff.game_over == False
    walkOff.situation.setInning(walkOff.at_bats[-1].get("about", {}).get("inning", -1))
    walkOff.situation.setTop(walkOff.at_bats[-1].get("about", {}).get("isTopInning", False))
    walkOff.process_at_bat_finished(walkOff.at_bats[-1])
    assert walkOff.game_over == True

    # TODO: home team wins with no walk off, no extras

def test_pitching_change_mid_at_bat():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/pitching_change_mid_at_bat.json")
    # Anthony Banda replaces Shohei Ohtani
    # at bat 30, 0=ball, 1=ball, 2=injury, 3=pitch_change, 4=defensive_switch, 5=ball
    process_at_bat(game, 29, None, None, None)
    assert game.situation.pitcher == "Shohei Ohtani"
    process_play_event(game.at_bats[30].get("playEvents", [])[0],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # ball
    assert game.situation.pitcher == "Shohei Ohtani"
    assert game.situation.pitchCount == 5
    assert game.situation.balls == 1
    assert game.situation.strikes == 0
    process_play_event(game.at_bats[30].get("playEvents", [])[1],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # ball
    assert game.situation.pitcher == "Shohei Ohtani"
    assert game.situation.pitchCount == 6
    assert game.situation.balls == 2
    assert game.situation.strikes == 0
    process_play_event(game.at_bats[30].get("playEvents", [])[2],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # injury
    assert game.situation.pitcher == "Shohei Ohtani"
    assert game.situation.pitchCount == 6
    assert game.situation.balls == 2
    assert game.situation.strikes == 0
    process_play_event(game.at_bats[30].get("playEvents", [])[3],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # pitching change
    assert game.situation.pitcher == "Anthony Banda"
    assert game.situation.pitchCount == 0
    assert game.situation.balls == 2
    assert game.situation.strikes == 0
    process_play_event(game.at_bats[30].get("playEvents", [])[4],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # defensive substitution
    assert game.situation.pitcher == "Anthony Banda"
    assert game.situation.pitchCount == 0
    assert game.situation.balls == 2
    assert game.situation.strikes == 0
    process_play_event(game.at_bats[30].get("playEvents", [])[5],
                     game.situation,
                     game.at_bats[30],
                     game,
                     None)  # ball
    assert game.situation.pitcher == "Anthony Banda"
    assert game.situation.pitchCount == 1
    assert game.situation.balls == 3
    assert game.situation.strikes == 0

def test_live_pitching_change():
    game = Game()
    game.get_game_by_file_path("tests/pitch_painter/data/live_pitching_change_mid_inning.json")
    # 0=mound_visit, 1=pitching_change
    process_at_bat(game, 64, None, None, None)
    # init pitcher manually for testing
    game.situation.setPitcher("Ben Joyce")
    game.cur_pitcher = "Ben Joyce"
    game.cur_home_pitcher = "Ben Joyce"
    assert game.situation.pitcher == "Ben Joyce"
    assert game.situation.outs == 2
    process_play_event(game.at_bats[-1].get("playEvents", [])[0],
                     game.situation,
                     game.at_bats[-1],
                     game,
                     None)  # mound visit
    assert game.situation.pitcher == "Ben Joyce"
    assert game.situation.outs == 2
    process_play_event(game.at_bats[-1].get("playEvents", [])[1],
                     game.situation,
                     game.at_bats[-1],
                     game,
                     None)  # pitching change
    assert game.situation.pitcher == "Sammy Peralta"
    assert game.situation.pitchCount == 0
    assert game.situation.balls == 0
    assert game.situation.strikes == 0
    assert game.situation.outs == 2