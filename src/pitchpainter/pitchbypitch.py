"""DEPRECATED: Delete? Draws and outputs the scoreboard for a pitch in a game."""


# TODO: DELETE THIS FILE WHEN COMFORTABLE!
# # pylint: disable=pointless-string-statement
# import datetime
# import json
# from pitchpainter.situation import Situation
# from pitchpainter.thread_poster import post_thread_text_as_image


# def draw_pitch_with_score(_away_score, _home_score, situation: Situation, alt_text=False):
#     """Draw a pitch with a score update added on run(s) scored. Use alt text spacing if specified."""
#     score_spacing = 12 if alt_text else 8
#     border = "+──────+" if alt_text else "+────────────+"
#     away_team = situation.away_team[:3].ljust(3)
#     away_score = str(_away_score)[:9].ljust(score_spacing)
#     home_team = situation.home_team[:3].ljust(3)
#     home_score = str(_home_score)[:8].ljust(score_spacing)
#     away_row = f"|{away_team} {away_score}|"
#     home_row = f"|{home_team} {home_score}|"
#     if alt_text:
#         away_row = f"| {away_team}  {away_score}|"
#         home_row = f"| {home_team}  {home_score}|"

#     # Pretty print all rows into a nice grid
#     output = (
#         f"{border}\n"
#         "|Score update|\n"
#         f"{away_row}\n"
#         f"{home_row}\n"
#         f"{border}"
#     )
#     pitch_text = draw_pitch(situation, alt_text)
#     return pitch_text + "\n" + output


# def draw_pitch(situation: Situation, alt_text=False):
#     """Draw a pitch given the situation with spacing used for stdout and image uploading for Threads posts.

#     Use alt text spacing if specified for a Threads post's alt text section.<br><br>
#     Symbols table:<br>
#     \u25C6=Filled diamond (base is occupied)<br>
#     \u25C7=Emtpy diamond (base is empty)<br>
#     \u25B2=Triangle up (top of the inning)<br>
#     \u25BC=Triangle down (bottom of the inning)<br>
#     \u25CF=Filled circle (out)<br>
#     \u25CB=Empty circle (no out)
#     """
#     # Shared data preparation and padding
#     away_team = situation.away_team[:3].ljust(3)
#     away_score = str(situation.away_score)[:9].ljust(9)
#     home_team = situation.home_team[:3].ljust(3)
#     home_score = str(situation.home_score)[:8].ljust(8)
#     inning = str(situation.inning)[:5].ljust(5)
#     balls = str(situation.balls)[:1]
#     strikes = str(situation.strikes)[:1].ljust(4)
#     pitcher = situation.pitcher
#     if len(pitcher) > 19:
#         pitcher = pitcher.split(" ")[1][:18]  # TODO: test this
#     pitcher = pitcher.ljust(18)
#     pitch_count = str(situation.pitch_count)[:4].ljust(4)

#     if not alt_text:
#         # pretty print stdout/image text layout
#         second_base = '\u25C6    ' if situation.baserunners[2] else '\u25C7    '
#         third_base = '\u25C6' if situation.baserunners[3] else '\u25C7'
#         first_base = '\u25C6   ' if situation.baserunners[1] else '\u25C7   '
#         inning_half = '\u25B2    ' if situation.top else '\u25BC    '
#         away_row = f"|{away_team} {away_score} {second_base} {inning_half if situation.top else inning}|"
#         home_row = f"|{home_team} {home_score} {third_base} {first_base} {inning if situation.top else inning_half}|"
#         one_out = f'            {"\u25CF" if situation.outs >= 1 else "\u25CB"}'
#         two_outs = '\u25CF' if situation.outs >= 2 else '\u25CB'
#         three_outs = '\u25CF ' if situation.outs >= 3 else '\u25CB '
#         count_row = f"|{one_out} {two_outs} {three_outs} {balls}-{strikes}|"
#         pitcher_row = f"|{pitcher} P:{pitch_count}|"
#         border = "+─────────────────────────+"
#         divider = "|─────────────────────────|"
#     else:
#         # Threads alt text/direct post as text instead of image layout
#         second_base = '\u25C6    ' if situation.baserunners[2] else '\u25C7    '
#         third_base = '\u25C6' if situation.baserunners[3] else '\u25C7'
#         first_base = '\u25C6   ' if situation.baserunners[1] else '\u25C7   '
#         inning_half = '\u25B2    ' if situation.top else '\u25BC    '
#         away_row = (
#             f"| {away_team} {away_score}       {second_base}       "
#             f"{inning_half if situation.top else inning}        |"
#         )
#         home_row = (
#             f"| {home_team}  {home_score}     {third_base}   {first_base}    "
#             f"{inning if situation.top else inning_half}        |"
#         )
#         one_out = f'            {"\u25CF" if situation.outs >= 1 else "\u25CB"}'
#         two_outs = '\u25CF' if situation.outs >= 2 else '\u25CB'
#         three_outs = '\u25CF ' if situation.outs >= 3 else '\u25CB '
#         count_row = f"|            {one_out} {two_outs} {three_outs}   {balls}-{strikes}      |"
#         pitcher_row = f"| {pitcher}        P: {pitch_count}       |"
#         border = "+─────────────+"
#         divider = "|─────────────|"

#     # Pretty print all rows into a nice grid
#     output = (
#         f"{border}\n"
#         f"{away_row}\n"
#         f"{home_row}\n"
#         f"{count_row}\n"
#         f"{divider}\n"
#         f"{pitcher_row}\n"
#         f"{border}"
#     )
#     return output


# def post_pitch_to_threads(situation: Situation,
#                           filepath,
#                           description="",
#                           away_score=-1,
#                           home_score=-1,
#                           scoring_play=False):
#     """Convert a situation to its desired output and call a post to Threads."""
#     if scoring_play and away_score > -1 and home_score > -1:
#         text = draw_pitch_with_score(away_score, home_score, situation, alt_text=False)
#         alt_text = draw_pitch_with_score(away_score, home_score, situation, alt_text=True)
#     else:
#         text = draw_pitch(situation, alt_text=False)
#         alt_text = draw_pitch(situation, alt_text=True)
#     post_thread_text_as_image(text, description_text=description, alt_text=alt_text, filepath=filepath)


# # TODO: remove testOut
# def print_all_pitches_from_game(game):
#     """Print all pitches of a game to stdout."""
#     test_out = ""
#     away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
#     home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
#     current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
#     situation = Situation()
#     situation.start_new_game(home_abbr, away_abbr, current_pitcher)
#     last_description = ""
#     current_play = game["liveData"]["plays"]["currentPlay"]
#     plays = game["liveData"]["plays"]["allPlays"]
#     play_idx = 0
#     i = 0
#     while not game.game_over:
#         current_play = game["liveData"]["plays"]["currentPlay"]
#         current_play = plays[play_idx]
#         live_description = current_play["result"]["description"]
#         if last_description != live_description:
#             last_description = live_description
#             situation.set_inning(current_play["about"]["inning"])
#             situation.set_top(current_play["about"]["isTopInning"])
#             # situation.setOuts(currentPlay["count"]["outs"])
#             situation.set_pitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

#             # Loop through all play events of current play - print when a pitch is thrown
#             for index, play_event in enumerate(current_play["playEvents"]):
#                 # Ignore if the event is not a pitch
#                 if not play_event["isPitch"]:
#                     continue

#                 # If this is the last pitch of the at bat
#                 if index == len(current_play["playEvents"]) - 1:
#                     # set score, baserunners, and outs
#                     situation.set_away_score(current_play["result"]["awayScore"])
#                     situation.set_home_score(current_play["result"]["homeScore"])
#                     situation.set_outs(current_play["count"]["outs"])
#                     # set balls and strikes to 0
#                     situation.set_balls(0)
#                     situation.set_strikes(0)
#                     situation.set_baserunners_at_end_of_at_bat(current_play)

#                 else:
#                     situation.set_balls(play_event["count"]["balls"])
#                     situation.set_strikes(play_event["count"]["strikes"])
#                     situation.set_outs(play_event["count"]["outs"])
#                     situation.set_baserunners_during_at_bat(current_play, play_event.get("index", -1))

#                 # Incrememnt pitch count for current pitcher
#                 pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
#                 pitch_count += 1
#                 game.pitch_count_dict[situation.pitcher] = pitch_count
#                 situation.set_pitch_count(pitch_count)

#                 print(f"{draw_pitch(situation)}\n")
#                 game_pk = game.get("gameData", {}).get("game", {}).get("pk", -1)
#                 play_id = play_event.get("playId", -1)
#                 now = datetime.datetime.now()
#                 cur_time = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
#                 filepath = f"images/{game_pk}/play_id_{play_id}_created_{cur_time}.png"
#                 post_pitch_to_threads(situation, filepath)
#                 if (
#                     situation.balls == 3
#                     and situation.strikes == 2
#                     and situation.outs == 2
#                     and situation.away_score == 0
#                     and situation.home_score == 3
#                     and situation.inning == 9
#                 ):
#                     test_out = draw_pitch(situation)
#                 i += 1

#             # Check if the result of this at bat finished the game
#             if situation.inning >= 9:
#                 if situation.outs >= 3:
#                     if situation.top:
#                         if situation.home_score > situation.away_score:
#                             game.game_over = True
#                     else:
#                         if situation.home_score != situation.away_score:
#                             game.game_over = True
#                 else:
#                     if not situation.top and situation.home_score > situation.away_score:
#                         game.game_over = True
#         play_idx += 1

#     border = ""
#     recap = ""
#     if situation.away_score > situation.home_score:
#         recap = (
#             f"|  Final score: {situation.away_score}-{situation.home_score}, "
#             f"{situation.away_team} over {situation.home_team}  |"
#         )
#     else:
#         recap = (
#             f"|  Final score: {situation.home_score}-{situation.away_score}, "
#             f"{situation.home_team} over {situation.away_team}  |"
#         )
#     while len(border) < len(recap):
#         border += "─"
#     border = "+" + border[1:-1] + "+"
#     print()
#     print(border)
#     print(recap)
#     print(border)
#     return test_out


# def list_all_pitches_from_game(game):
#     """Return a list of all pitches from a game."""
#     out = []
#     away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
#     home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
#     current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
#     situation = Situation(home_abbr, away_abbr, current_pitcher)
#     last_description = ""
#     current_play = game["liveData"]["plays"]["currentPlay"]
#     plays = game["liveData"]["plays"]["allPlays"]
#     play_idx = 0
#     i = 0
#     while not game._over:
#         current_play = game["liveData"]["plays"]["currentPlay"]
#         current_play = plays[play_idx]
#         live_description = current_play["result"]["description"]
#         if last_description != live_description:
#             last_description = live_description
#             situation.set_inning(current_play["about"]["inning"])
#             situation.set_top(current_play["about"]["isTopInning"])
#             # situation.setOuts(currentPlay["count"]["outs"])
#             situation.set_pitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

#             # Loop through all play events of current play - print when a pitch is thrown
#             for index, play_event in enumerate(current_play["playEvents"]):
#                 # Ignore if the event is not a pitch
#                 if not play_event["isPitch"]:
#                     continue

#                 # If this is the last pitch of the at bat
#                 if index == len(current_play["playEvents"]) - 1:
#                     # set score, baserunners, and outs
#                     situation.set_away_score(current_play["result"]["awayScore"])
#                     situation.set_home_score(current_play["result"]["homeScore"])
#                     situation.set_outs(current_play["count"]["outs"])
#                     # set balls and strikes to 0
#                     situation.set_balls(0)
#                     situation.set_strikes(0)
#                     situation.setBaserunnersFromPlay(current_play)

#                 else:
#                     situation.set_balls(play_event["count"]["balls"])
#                     situation.set_strikes(play_event["count"]["strikes"])
#                     situation.set_outs(play_event["count"]["outs"])

#                 # Incrememnt pitch count for current pitcher
#                 pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
#                 pitch_count += 1
#                 game.pitch_count_dict[situation.pitcher] = pitch_count
#                 situation.set_pitch_count(pitch_count)

#                 out.append(draw_pitch(situation))
#                 i += 1

#             # Check if the result of this at bat finished the game
#             if situation.inning >= 9:
#                 if situation.outs >= 3:
#                     if situation.top:
#                         if situation.home_score > situation.away_score:
#                             game.game_over = True
#                     else:
#                         if situation.home_score != situation.away_score:
#                             game.game_over = True
#                 else:
#                     if not situation.top and situation.home_score > situation.away_score:
#                         game.game_over = True
#         play_idx += 1

#     border = ""
#     recap = ""
#     if situation.away_score > situation.home_score:
#         recap = (
#             f"|  Final score: {situation.away_score}-{situation.home_score}, "
#             f"{situation.away_team} over {situation.home_team}  |"
#         )
#     else:
#         recap = (
#             f"|  Final score: {situation.home_score}-{situation.away_score}, "
#             f"{situation.home_team} over {situation.away_team}  |"
#         )
#     while len(border) < len(recap):
#         border += "─"
#     border = "+" + border[1:-1] + "+"
#     out.append("\n")
#     out.append(border)
#     out.append(recap)
#     out.append(border)
#     return out


# def print_live_game(game):
#     """Print all pitches from a live game to stdout."""
#     away_abbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
#     home_abbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
#     current_pitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
#     situation = Situation(home_abbr, away_abbr, current_pitcher)
#     last_description = ""
#     current_play = game["liveData"]["plays"]["currentPlay"]
#     while not game.game_over:
#         current_play = game["liveData"]["plays"]["currentPlay"]
#         live_description = last_description
#         if last_description == live_description:
#             last_description = live_description
#             situation.set_inning(current_play["about"]["inning"])
#             situation.set_top(current_play["about"]["isTopInning"])
#             situation.set_pitcher(current_play["matchup"]["pitcher"]["fullName"])  # José Quijada

#             print(f"{current_play["matchup"]["batter"]["fullName"]} now batting.")

#             # Loop through all play events of current play - print when a pitch is thrown
#             for index, play_event in enumerate(current_play["playEvents"]):
#                 # Ignore if the event is not a pitch
#                 if not play_event["isPitch"]:
#                     continue

#                 # If this is the last pitch of the at bat
#                 if index == len(current_play["playEvents"]) - 1:
#                     # set score, baserunners, and outs
#                     situation.set_away_score(current_play["result"]["awayScore"])
#                     situation.set_home_score(current_play["result"]["homeScore"])
#                     situation.set_outs(current_play["count"]["outs"])
#                     # set balls and strikes to 0
#                     situation.set_balls(0)
#                     situation.set_strikes(0)
#                     situation.setBaserunnersFromPlay(current_play)

#                     print(live_description)
#                 else:
#                     situation.set_balls(play_event["count"]["balls"])
#                     situation.set_strikes(play_event["count"]["strikes"])
#                     if play_event["details"]["isStrike"]:
#                         print(f"{play_event["details"]["description"]} {situation.strikes}.")
#                     elif play_event["details"]["isBall"]:
#                         print(f"{play_event["details"]["description"]} {situation.balls}.")

#                 # Incrememnt pitch count for current pitcher
#                 pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
#                 pitch_count += 1
#                 game.pitch_count_dict[situation.pitcher] = pitch_count
#                 situation.set_pitch_count(pitch_count)

#                 print(f"{draw_pitch(situation)}\n")

#             # Check if the result of this at bat finished the game
#             if situation.outs >= 3 and situation.inning >= 9:
#                 if situation.top:
#                     if situation.home_score > situation.away_score:
#                         game.game_over = True
#                 else:
#                     if situation.home_score != situation.away_score:
#                         game.game_over = True

#     border = ""
#     recap = ""
#     if situation.away_score > situation.home_score:
#         recap = (
#             f"|  Final score: {situation.away_score}-{situation.home_score}, "
#             f"{situation.away_team} over {situation.home_team}  |"
#         )
#     else:
#         recap = (
#             f"|  Final score: {situation.home_score}-{situation.away_score}, "
#             f"{situation.home_team} over {situation.away_team}  |"
#         )
#     while len(border) < len(recap):
#         border += "─"
#     border = "+" + border[1:-1] + "+"
#     print()
#     print(border)
#     print(recap)
#     print(border)


# # TODO: move these tests to actual pytest test functions in tests/pitch_painter/test_*.py
# def main():
#     """Run this file's code."""
#     '''
#     +==============================================+
#     |   Testing on all games for a specific date   |
#     +==============================================+
#     '''
#     # gamesList = []
#     # schedule = statsapi.get('schedule', {'sportId': 1, 'date': '2025-09-11'})
#     # gameList = schedule["dates"][0]["games"]
#     # for i in gameList:
#     #     gamesList.append(statsapi.get('game', {'gamePk': i["gamePk"]}))
#     # print(f"Games for {schedule["dates"][0]["date"]}:")
#     # for i in gamesList:
#     #     print(f"{i["gameData"]["teams"]["away"]["name"]} @ {i["gameData"]["teams"]["home"]["name"]}")
#     # print()

#     # game = statsapi.get('game', {'gamePk': 776368})
#     # awayTeam = game["gameData"]["teams"]["away"]["name"]
#     # homeTeam = game["gameData"]["teams"]["home"]["name"]
#     # situation = Situation(homeTeam, awayTeam)
#     # drawPitch(situation)
#     # print("Home:", homeTeam)
#     # print("Away:", awayTeam)
#     # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
#     # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
#     # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
#     # print("Count:", currentCount)
#     # print("Batter:", currentBatter)
#     # print("Pitcher:", currentPitcher)

#     '''
#     +=======================================+
#     |   Testing on custom situation input   |
#     +=======================================+
#     '''
#     # print(game["liveData"]["leaders"])
#     # situation = Situation("SD", "DET", "Robert Suarez")
#     # situation.setPitchCount(25)
#     # situation.setHomeScore(3)
#     # situation.setBaserunners([1, 2, 3])
#     # for i in range(9):
#     #     situation.setOuts(random.randint(1, 3))
#     #     situation.setBalls(random.randint(0, 3))
#     #     situation.setStrikes(random.randint(0, 2))
#     #     situation.setInning(i + 1)
#     #     drawPitch(situation)
#     #     time.sleep(random.randint(1, 2))

#     '''
#     +============================================================================================================+
#     |   Testing on example_out.json (when no wifi so no api calls can happen) - very niche but now's that time   |
#     +============================================================================================================+
#     '''
#     # with open("example_out.json", "r") as f:
#     #     game = json.load(f)
#     # # print(game)
#     # awayTeam = game["gameData"]["teams"]["away"]["name"] # Los Angeles Angels
#     # homeTeam = game["gameData"]["teams"]["home"]["name"] # Houston Astros
#     # awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
#     # homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
#     # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
#     # situation = Situation(homeAbbr, awayAbbr, currentPitcher)
#     # drawPitch(situation)
#     # print("Home:", homeTeam)
#     # print("Away:", awayTeam)
#     # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
#     # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
#     # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
#     # print("Count:", currentCount)
#     # print("Batter:", currentBatter)
#     # print("Pitcher:", currentPitcher)

#     '''
#     +=========================+
#     |   Current Play Output   |
#     +=========================+
#     '''
#     # game = statsapi.get('game', {'gamePk': 776368})
#     with open("meadows.json", "r", encoding='utf-8') as f:
#         game = json.load(f)
#     print_all_pitches_from_game(game)

#     '''
#     +======================+
#     |   Live Play Output   |
#     +======================+
#     '''
#     # game = statsapi.get('game', {'gamePk': 776189})
#     # # with open("meadows.json", "r") as f:
#     # # # with open("example_out.json", "r") as f:
#     # #     game = json.load(f)
#     # printLiveGame(game)


# if __name__ == '__main__':
#     main()
