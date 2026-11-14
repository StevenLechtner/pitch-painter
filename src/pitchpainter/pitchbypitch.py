"""Draws and outputs the scoreboard for a pitch in a game."""


# TODO: Major code cleanup with this file. Is this file even needed any more, or does live_game.py do it all...
# pylint: disable=pointless-string-statement
import datetime
import json
from pitchpainter.situation import Situation
from pitchpainter.thread_poster import postThreadTextAsImage


def draw_pitch_for_tweeting(situation: Situation):
    """Draw a pitch given the situation with spacing to best match altText in Threads."""
    # Away team row logic
    away_team = situation.awayTeam[:3]
    while len(away_team) < 3:
        away_team += " "
    away_score = str(situation.awayScore)[:9]
    while len(away_score) < 9:
        away_score += " "
    second_base = '\u25C6    ' if situation.baserunners[2] else '\u25C7    '  # Diamond
    inning_half = '\u25B2    ' if situation.top else '\u25BC    '  # Triangle
    inning = str(situation.inning)[:5]
    while len(inning) < 5:
        inning += " "
    if situation.top:
        away_row = f"| {away_team} {away_score}       {second_base}      {inning_half}        |"
    else:
        away_row = f"| {away_team} {away_score}       {second_base}       {inning}        |"

    # Home team row logic
    home_team = situation.homeTeam[:3]
    while len(home_team) < 3:
        home_team += " "
    home_score = str(situation.homeScore)[:8]
    while len(home_score) < 8:
        home_score += " "
    third_base = '\u25C6' if situation.baserunners[3] else '\u25C7'  # Diamond
    first_base = '\u25C6   ' if situation.baserunners[1] else '\u25C7   '  # Diamond
    if situation.top:
        home_row = f"| {home_team}  {home_score}     {third_base}   {first_base}    {inning}        |"
    else:
        home_row = f"| {home_team}  {home_score}     {third_base}   {first_base}    {inning_half}        |"

    # Count row logic
    one_out = '            \u25CF' if situation.outs >= 1 else '            \u25CB'  # Circle
    two_outs = '\u25CF' if situation.outs >= 2 else '\u25CB'  # Circle
    three_outs = '\u25CF ' if situation.outs >= 3 else '\u25CB '  # Circle
    balls = str(situation.balls)[:1]
    strikes = str(situation.strikes)[:1]
    while len(strikes) < 4:
        strikes += " "
    count_row = f"|            {one_out} {two_outs} {three_outs}   {balls}-{strikes}      |"

    # Pitcher row logic
    pitcher = situation.pitcher
    if len(pitcher) > 19:
        pitcher = pitcher.split(" ")[1][:18]
    while len(pitcher) < 18:
        pitcher += " "
    pitch_count = str(situation.pitchCount)[:4]
    while len(pitch_count) < 4:
        pitch_count += " "
    pitcher_row = f"| {pitcher}        P: {pitch_count}       |"

    # Pretty print all rows into a nice grid of 27 chars per row
    output = (
        "+─────────────+\n"
        f"{away_row}\n"
        f"{home_row}\n"
        f"{count_row}\n"
        "|─────────────|\n"
        f"{pitcher_row}\n"
        "+─────────────+"
    )
    return output


def draw_pitch_with_score_alt_text(_away_score, _home_score, situation):
    """Draw a score update to add to a scoreboard post on run(s) scored."""
    away_team = situation.awayTeam[:3]
    while len(away_team) < 3:
        away_team += " "
    away_score = str(_away_score)[:9]
    while len(away_score) < 12:
        away_score += " "
    home_team = situation.homeTeam[:3]
    while len(home_team) < 3:
        home_team += " "
    home_score = str(_home_score)[:8]
    while len(home_score) < 12:
        home_score += " "

    away_row = f"| {away_team}  {away_score}|"
    home_row = f"| {home_team}  {home_score}|"

    # Pretty print all rows into a nice grid of 14 chars per row
    output = (
        "+──────+\n"
        "|Score update|\n"
        f"{away_row}\n"
        f"{home_row}\n"
        "+──────+"
    )
    return draw_pitch_for_tweeting(situation) + "\n" + output


# FIXME: extra innings look off centered
def draw_pitch(situation: Situation):
    """Draw a pitch given the situation with spacing used for image uploading - the actual Threads image contents."""
    # Away team row logic
    away_team = situation.awayTeam[:3]
    while len(away_team) < 3:
        away_team += " "
    away_score = str(situation.awayScore)[:9]
    while len(away_score) < 9:
        away_score += " "
    second_base = '\u25C6    ' if situation.baserunners[2] else '\u25C7    '  # Diamond
    inning_half = '\u25B2    ' if situation.top else '\u25BC    '  # Triangle
    inning = str(situation.inning)[:5]
    while len(inning) < 5:
        inning += " "
    if situation.top:
        away_row = f"|{away_team} {away_score} {second_base} {inning_half}|"
    else:
        away_row = f"|{away_team} {away_score} {second_base} {inning}|"

    # Home team row logic
    home_team = situation.homeTeam[:3]
    while len(home_team) < 3:
        home_team += " "
    home_score = str(situation.homeScore)[:8]
    while len(home_score) < 8:
        home_score += " "
    third_base = '\u25C6' if situation.baserunners[3] else '\u25C7'  # Diamond
    first_base = '\u25C6   ' if situation.baserunners[1] else '\u25C7   '  # Diamond
    if situation.top:
        home_row = f"|{home_team} {home_score} {third_base} {first_base} {inning}|"
    else:
        home_row = f"|{home_team} {home_score} {third_base} {first_base} {inning_half}|"

    # Count row logic
    one_out = '            \u25CF' if situation.outs >= 1 else '            \u25CB'  # Circle
    two_outs = '\u25CF' if situation.outs >= 2 else '\u25CB'  # Circle
    three_outs = '\u25CF ' if situation.outs >= 3 else '\u25CB '  # Circle
    balls = str(situation.balls)[:1]
    strikes = str(situation.strikes)[:1]
    while len(strikes) < 4:
        strikes += " "
    count_row = f"|{one_out} {two_outs} {three_outs} {balls}-{strikes}|"

    # Pitcher row logic
    pitcher = situation.pitcher
    if len(pitcher) > 19:
        pitcher = pitcher.split(" ")[1][:18]
    while len(pitcher) < 18:
        pitcher += " "
    pitch_count = str(situation.pitchCount)[:4]
    while len(pitch_count) < 4:
        pitch_count += " "
    pitcher_row = f"|{pitcher} P:{pitch_count}|"

    # Pretty print all rows into a nice grid of 27 chars per row
    output = (
        "+─────────────────────────+\n"
        f"{away_row}\n"
        f"{home_row}\n"
        f"{count_row}\n"
        "|─────────────────────────|\n"
        f"{pitcher_row}\n"
        "+─────────────────────────+"
    )
    return output


def draw_pitch_with_score_update(_away_score, _home_score, situation):
    """Draw a pitch with a score update added on run(s) scored."""
    away_team = situation.awayTeam[:3]
    while len(away_team) < 3:
        away_team += " "
    away_score = str(_away_score)[:9]
    while len(away_score) < 8:
        away_score += " "
    home_team = situation.homeTeam[:3]
    while len(home_team) < 3:
        home_team += " "
    home_score = str(_home_score)[:8]
    while len(home_score) < 8:
        home_score += " "

    away_row = f"|{away_team} {away_score}|"
    home_row = f"|{home_team} {home_score}|"

    # Pretty print all rows into a nice grid of 14 chars per row
    output = (
        "+────────────+\n"
        "|Score update|\n"
        f"{away_row}\n"
        f"{home_row}\n"
        "+────────────+"
    )
    return draw_pitch(situation) + "\n" + output


def post_pitch_to_threads(situation: Situation,
                          filepath,
                          description="",
                          away_score=-1,
                          home_score=-1,
                          scoring_play=False):
    """Convert a situation to its desired output and call a post to Threads."""
    if scoring_play and away_score > -1 and home_score > -1:
        text = draw_pitch_with_score_update(away_score, home_score, situation)
        alt_text = draw_pitch_with_score_alt_text(away_score, home_score, situation)
    else:
        text = draw_pitch(situation)
        alt_text = draw_pitch_for_tweeting(situation)
    postThreadTextAsImage(text, descriptionText=description, altText=alt_text, filepath=filepath)


# TODO: remove testOut
def print_all_pitches_from_game(game):
    """Print all pitches of a game to stdout."""
    test_out = ""
    away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
    home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
    current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
    situation = Situation()
    situation.startNewGame(home_abbr, away_abbr, current_pitcher)
    last_description = ""
    current_play = game["liveData"]["plays"]["currentPlay"]
    plays = game["liveData"]["plays"]["allPlays"]
    play_idx = 0
    i = 0
    while not game.game_over:
        current_play = game["liveData"]["plays"]["currentPlay"]
        current_play = plays[play_idx]
        live_description = current_play["result"]["description"]
        if last_description != live_description:
            last_description = live_description
            situation.setInning(current_play["about"]["inning"])
            situation.setTop(current_play["about"]["isTopInning"])
            # situation.setOuts(currentPlay["count"]["outs"])
            situation.setPitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

            # Loop through all play events of current play - print when a pitch is thrown
            for index, play_event in enumerate(current_play["playEvents"]):
                # Ignore if the event is not a pitch
                if not play_event["isPitch"]:
                    continue

                # If this is the last pitch of the at bat
                if index == len(current_play["playEvents"]) - 1:
                    # set score, baserunners, and outs
                    situation.setAwayScore(current_play["result"]["awayScore"])
                    situation.setHomeScore(current_play["result"]["homeScore"])
                    situation.setOuts(current_play["count"]["outs"])
                    # set balls and strikes to 0
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersAtEndOfAtBat(current_play)

                else:
                    situation.setBalls(play_event["count"]["balls"])
                    situation.setStrikes(play_event["count"]["strikes"])
                    situation.setOuts(play_event["count"]["outs"])
                    situation.setBaserunnersDuringAtBat(current_play, play_event.get("index", -1))

                # Incrememnt pitch count for current pitcher
                pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
                pitch_count += 1
                game.pitch_count_dict[situation.pitcher] = pitch_count
                situation.setPitchCount(pitch_count)

                print(f"{draw_pitch(situation)}\n")
                game_pk = game.get("gameData", {}).get("game", {}).get("pk", -1)
                play_id = play_event.get("playId", -1)
                now = datetime.datetime.now()
                cur_time = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
                filepath = f"images/{game_pk}/play_id_{play_id}_created_{cur_time}.png"
                post_pitch_to_threads(situation, filepath)
                if (
                    situation.balls == 3
                    and situation.strikes == 2
                    and situation.outs == 2
                    and situation.awayScore == 0
                    and situation.homeScore == 3
                    and situation.inning == 9
                ):
                    test_out = draw_pitch(situation)
                i += 1

            # Check if the result of this at bat finished the game
            if situation.inning >= 9:
                if situation.outs >= 3:
                    if situation.top:
                        if situation.homeScore > situation.awayScore:
                            game.game_over = True
                    else:
                        if situation.homeScore != situation.awayScore:
                            game.game_over = True
                else:
                    if not situation.top and situation.homeScore > situation.awayScore:
                        game.game_over = True
        play_idx += 1

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = (
            f"|  Final score: {situation.awayScore}-{situation.homeScore}, "
            f"{situation.awayTeam} over {situation.homeTeam}  |"
        )
    else:
        recap = (
            f"|  Final score: {situation.homeScore}-{situation.awayScore}, "
            f"{situation.homeTeam} over {situation.awayTeam}  |"
        )
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    print()
    print(border)
    print(recap)
    print(border)
    return test_out


def list_all_pitches_from_game(game):
    """Return a list of all pitches from a game."""
    out = []
    away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
    home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
    current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
    situation = Situation(home_abbr, away_abbr, current_pitcher)
    last_description = ""
    current_play = game["liveData"]["plays"]["currentPlay"]
    plays = game["liveData"]["plays"]["allPlays"]
    play_idx = 0
    i = 0
    while not game._over:
        current_play = game["liveData"]["plays"]["currentPlay"]
        current_play = plays[play_idx]
        live_description = current_play["result"]["description"]
        if last_description != live_description:
            last_description = live_description
            situation.setInning(current_play["about"]["inning"])
            situation.setTop(current_play["about"]["isTopInning"])
            # situation.setOuts(currentPlay["count"]["outs"])
            situation.setPitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

            # Loop through all play events of current play - print when a pitch is thrown
            for index, play_event in enumerate(current_play["playEvents"]):
                # Ignore if the event is not a pitch
                if not play_event["isPitch"]:
                    continue

                # If this is the last pitch of the at bat
                if index == len(current_play["playEvents"]) - 1:
                    # set score, baserunners, and outs
                    situation.setAwayScore(current_play["result"]["awayScore"])
                    situation.setHomeScore(current_play["result"]["homeScore"])
                    situation.setOuts(current_play["count"]["outs"])
                    # set balls and strikes to 0
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersFromPlay(current_play)

                else:
                    situation.setBalls(play_event["count"]["balls"])
                    situation.setStrikes(play_event["count"]["strikes"])
                    situation.setOuts(play_event["count"]["outs"])

                # Incrememnt pitch count for current pitcher
                pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
                pitch_count += 1
                game.pitch_count_dict[situation.pitcher] = pitch_count
                situation.setPitchCount(pitch_count)

                out.append(draw_pitch(situation))
                i += 1

            # Check if the result of this at bat finished the game
            if situation.inning >= 9:
                if situation.outs >= 3:
                    if situation.top:
                        if situation.homeScore > situation.awayScore:
                            game.game_over = True
                    else:
                        if situation.homeScore != situation.awayScore:
                            game.game_over = True
                else:
                    if not situation.top and situation.homeScore > situation.awayScore:
                        game.game_over = True
        play_idx += 1

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = (
            f"|  Final score: {situation.awayScore}-{situation.homeScore}, "
            f"{situation.awayTeam} over {situation.homeTeam}  |"
        )
    else:
        recap = (
            f"|  Final score: {situation.homeScore}-{situation.awayScore}, "
            f"{situation.homeTeam} over {situation.awayTeam}  |"
        )
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    out.append("\n")
    out.append(border)
    out.append(recap)
    out.append(border)
    return out


def print_live_game(game):
    """Print all pitches from a live game to stdout."""
    away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
    home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
    current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
    situation = Situation(home_abbr, away_abbr, current_pitcher)
    last_description = ""
    current_play = game["liveData"]["plays"]["currentPlay"]
    while not game.game_over:
        current_play = game["liveData"]["plays"]["currentPlay"]
        live_description = last_description
        if last_description == live_description:
            last_description = live_description
            situation.setInning(current_play["about"]["inning"])
            situation.setTop(current_play["about"]["isTopInning"])
            situation.setPitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

            print(f"{current_play["matchup"]["batter"]["fullName"]} now batting.")

            # Loop through all play events of current play - print when a pitch is thrown
            for index, play_event in enumerate(current_play["playEvents"]):
                # Ignore if the event is not a pitch
                if not play_event["isPitch"]:
                    continue

                # If this is the last pitch of the at bat
                if index == len(current_play["playEvents"]) - 1:
                    # set score, baserunners, and outs
                    situation.setAwayScore(current_play["result"]["awayScore"])
                    situation.setHomeScore(current_play["result"]["homeScore"])
                    situation.setOuts(current_play["count"]["outs"])
                    # set balls and strikes to 0
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersFromPlay(current_play)

                    print(live_description)
                else:
                    situation.setBalls(play_event["count"]["balls"])
                    situation.setStrikes(play_event["count"]["strikes"])
                    if play_event["details"]["isStrike"]:
                        print(f"{play_event["details"]["description"]} {situation.strikes}.")
                    elif play_event["details"]["isBall"]:
                        print(f"{play_event["details"]["description"]} {situation.balls}.")

                # Incrememnt pitch count for current pitcher
                pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
                pitch_count += 1
                game.pitch_count_dict[situation.pitcher] = pitch_count
                situation.setPitchCount(pitch_count)

                print(f"{draw_pitch(situation)}\n")

            # Check if the result of this at bat finished the game
            if situation.outs >= 3 and situation.inning >= 9:
                if situation.top:
                    if situation.homeScore > situation.awayScore:
                        game.game_over = True
                else:
                    if situation.homeScore != situation.awayScore:
                        game.game_over = True

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = (
            f"|  Final score: {situation.awayScore}-{situation.homeScore}, "
            f"{situation.awayTeam} over {situation.homeTeam}  |"
        )
    else:
        recap = (
            f"|  Final score: {situation.homeScore}-{situation.awayScore}, "
            f"{situation.homeTeam} over {situation.awayTeam}  |"
        )
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    print()
    print(border)
    print(recap)
    print(border)


# TODO: move these tests to actual pytest test functions in tests/pitch_painter/test_*.py
def main():
    """Run this file's code."""
    '''
    +==============================================+
    |   Testing on all games for a specific date   |
    +==============================================+
    '''
    # gamesList = []
    # schedule = statsapi.get('schedule', {'sportId': 1, 'date': '2025-09-11'})
    # gameList = schedule["dates"][0]["games"]
    # for i in gameList:
    #     gamesList.append(statsapi.get('game', {'gamePk': i["gamePk"]}))
    # print(f"Games for {schedule["dates"][0]["date"]}:")
    # for i in gamesList:
    #     print(f"{i["gameData"]["teams"]["away"]["name"]} @ {i["gameData"]["teams"]["home"]["name"]}")
    # print()

    # game = statsapi.get('game', {'gamePk': 776368})
    # awayTeam = game["gameData"]["teams"]["away"]["name"]
    # homeTeam = game["gameData"]["teams"]["home"]["name"]
    # situation = Situation(homeTeam, awayTeam)
    # drawPitch(situation)
    # print("Home:", homeTeam)
    # print("Away:", awayTeam)
    # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
    # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
    # print("Count:", currentCount)
    # print("Batter:", currentBatter)
    # print("Pitcher:", currentPitcher)

    '''
    +=======================================+
    |   Testing on custom situation input   |
    +=======================================+
    '''
    # print(game["liveData"]["leaders"])
    # situation = Situation("SD", "DET", "Robert Suarez")
    # situation.setPitchCount(25)
    # situation.setHomeScore(3)
    # situation.setBaserunners([1, 2, 3])
    # for i in range(9):
    #     situation.setOuts(random.randint(1, 3))
    #     situation.setBalls(random.randint(0, 3))
    #     situation.setStrikes(random.randint(0, 2))
    #     situation.setInning(i + 1)
    #     drawPitch(situation)
    #     time.sleep(random.randint(1, 2))

    '''
    +============================================================================================================+
    |   Testing on example_out.json (when no wifi so no api calls can happen) - very niche but now's that time   |
    +============================================================================================================+
    '''
    # with open("example_out.json", "r") as f:
    #     game = json.load(f)
    # # print(game)
    # awayTeam = game["gameData"]["teams"]["away"]["name"] # Los Angeles Angels
    # homeTeam = game["gameData"]["teams"]["home"]["name"] # Houston Astros
    # awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    # homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    # situation = Situation(homeAbbr, awayAbbr, currentPitcher)
    # drawPitch(situation)
    # print("Home:", homeTeam)
    # print("Away:", awayTeam)
    # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
    # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
    # print("Count:", currentCount)
    # print("Batter:", currentBatter)
    # print("Pitcher:", currentPitcher)

    '''
    +=========================+
    |   Current Play Output   |
    +=========================+
    '''
    # game = statsapi.get('game', {'gamePk': 776368})
    with open("meadows.json", "r", encoding='utf-8') as f:
        game = json.load(f)
    print_all_pitches_from_game(game)

    '''
    +======================+
    |   Live Play Output   |
    +======================+
    '''
    # game = statsapi.get('game', {'gamePk': 776189})
    # # with open("meadows.json", "r") as f:
    # # # with open("example_out.json", "r") as f:
    # #     game = json.load(f)
    # printLiveGame(game)


if __name__ == '__main__':
    main()
