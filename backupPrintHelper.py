'''
Print all pitches from game alt:
'''
# awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
# homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
# currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
# situation = Situation(homeAbbr, awayAbbr, currentPitcher)
# lastDescription = ""
# currentPlay = game["liveData"]["plays"]["currentPlay"]
# plays = game["liveData"]["plays"]["allPlays"]
# playIdx = 0
# totalPitches = 0
# while not situation.gameOver:
#     currentPlay = game["liveData"]["plays"]["currentPlay"]
#     currentPlay = plays[playIdx]
#     liveDescription = currentPlay["result"]["description"]
#     # print(liveDescription)
#     if (lastDescription != liveDescription):
#         lastDescription = liveDescription
#         # situation.setAwayScore(currentPlay["result"]["awayScore"])
#         # situation.setHomeScore(currentPlay["result"]["homeScore"])
#         # situation.setOuts(currentPlay["count"]["outs"])
#         # situation.setBalls(currentPlay["count"]["balls"])
#         # situation.setStrikes(currentPlay["count"]["strikes"])
#         situation.setInning(currentPlay["about"]["inning"])
#         situation.setTop(currentPlay["about"]["isTopInning"])
#         situation.setPitcher(currentPlay["matchup"]["pitcher"]["fullName"]) # José Quijada
#         print(f"{currentPlay["matchup"]["batter"]["fullName"]} now batting.")
#         runners = currentPlay["runners"]

#         # THIS IS ALMOST GOOD, LOOK AT TOP 4 FIRST TO THIRD
#         # basesOccupied = situation.baserunners
#         # if situation.outs < 3:
#         #     for runner in runners:
#         #         if runner["movement"]["end"] is not None:
#         #             # 1B, 2B, 3B, 4B, or score - ignore if score.
#         #             try:
#         #                 runnerLoc = int(runner["movement"]["end"][:1])
#         #                 basesOccupied[runnerLoc] = True
#         #             except:
#         #                 pass
#         #             # remove start base
#         #             try:
#         #                 startBase = int(runner["movement"]["start"][:1])
#         #                 if startBase is not None:
#         #                     basesOccupied[startBase] = False
#         #             except:
#         #                 pass
                
#         #             # print(runnerLoc)
#         #             # basesOccupied[runnerLoc] = True
#         #         outBase = runner["movement"]["outBase"]
#         #         if outBase is not None:
#         #             # print(outBase)
#         #             startBase = None
#         #             if outBase is not None:
#         #                 try:
#         #                     startBase = int(runner["movement"]["start"][:1])
#         #                     # print(startBase)
#         #                 except:
#         #                     continue
#         #             if startBase is not None:
#         #                 basesOccupied[startBase] = False
#         # else:
#         #     basesOccupied = {1: False, 2: False, 3: False}
#         # COMMENT OUT FOR HELP
#         # for key, val in basesOccupied.items():
#         #     print(key, val, end=" ")
#         # print()
#         # situation.setBaserunners(basesOccupied)
#         # THIS WORKS PERFECT BUT HAS NO "LOGIC" TO IT
#         # basesOccupied = {1: False, 2: False, 3: False}
#         # if situation.outs < 3:
#         #     if currentPlay["matchup"].get("postOnFirst"):
#         #         basesOccupied[1] = True
#         #     if currentPlay["matchup"].get("postOnSecond"):
#         #         basesOccupied[2] = True
#         #     if currentPlay["matchup"].get("postOnThird"):
#         #         basesOccupied[3] = True
#         # situation.setBaserunners(basesOccupied)

#         # pitchesToCurrBatter = len(currentPlay["pitchIndex"])
#         # pitchCount = situation.pitchCount.get(situation.pitcher, 0)
#         # pitchCount += pitchesToCurrBatter
#         # situation.pitchCount[situation.pitcher] = pitchCount

#         # drawPitch(situation)
#         # if situation.outs >= 3 and situation.inning >= 9:
#         #     if situation.top:
#         #         if situation.homeScore > situation.awayScore:
#         #             situation.gameOver = True
#         #     else:
#         #         if situation.homeScore != situation.awayScore:
#         #             situation.gameOver = True

#     lastPitch = False
#     for index, playEvent in enumerate(currentPlay["playEvents"]):
#         if index == len(currentPlay["playEvents"]) - 1:
#             lastPitch = True
#             situation.setAwayScore(currentPlay["result"]["awayScore"])
#             situation.setHomeScore(currentPlay["result"]["homeScore"])
#             situation.setOuts(currentPlay["count"]["outs"])
#             situation.setBalls(0)
#             situation.setStrikes(0)
#             basesOccupied = {1: False, 2: False, 3: False}
#             if situation.outs < 3:
#                 if currentPlay["matchup"].get("postOnFirst"):
#                     basesOccupied[1] = True
#                 if currentPlay["matchup"].get("postOnSecond"):
#                     basesOccupied[2] = True
#                 if currentPlay["matchup"].get("postOnThird"):
#                     basesOccupied[3] = True
#             situation.setBaserunners(basesOccupied)
#             print(liveDescription)
#         if playEvent["isPitch"]:
#             totalPitches += 1
#             # situation.setOuts(playEvent["count"]["outs"])
#             if not lastPitch:
#                 situation.setBalls(playEvent["count"]["balls"])
#                 situation.setStrikes(playEvent["count"]["strikes"])
#                 if playEvent["details"]["isStrike"]:
#                     print(f"{playEvent["details"]["description"]} {situation.strikes}.")
#                 elif playEvent["details"]["isBall"]:
#                     print(f"{playEvent["details"]["description"]} {situation.balls}.")
#             # print(situation.pitcher)
#             pitchCount = situation.pitchCount.get(situation.pitcher, 0)
#             pitchCount += 1
#             situation.pitchCount[situation.pitcher] = pitchCount
#             drawPitch(situation)

#     if situation.outs >= 3 and situation.inning >= 9:
#         if situation.top:
#             if situation.homeScore > situation.awayScore:
#                 situation.gameOver = True
#         else:
#             if situation.homeScore != situation.awayScore:
#                 situation.gameOver = True
#     playIdx += 1
# asdf = 0
# # for key,val in situation.pitchCount.items():
# #     print(key, val)
# #     asdf += val
# # print(totalPitches)
# # print(asdf)
# if situation.awayScore > situation.homeScore:
#     print(f"Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}")
# else:
#     print(f"Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}")
