import statsapi
import time
from pitchbypitch import Situation, drawPitch

desiredTeam = 'Detroit Tigers'

def getGamePk():
    schedule = statsapi.get('schedule', {'sportId': 1})
    today = '2026-05-18'
    for date in schedule['dates']:
        if date['date'] == today:
            games = date['games']
            for game in games:
                gamePk = game['gamePk']
                teams = getTeamsByGame(gamePk)
                if (desiredTeam in teams):
                    print(f"Away: {teams[1]}")
                    print(f"Home: {teams[0]}")
                    print(f"gamePk: {gamePk}")
                    print()
                    return gamePk
    return -1

def getTeamsByGame(gamePk):
    game = statsapi.get('game', {'gamePk': gamePk})
    homeId = game["gameData"]["teams"]["home"]["id"]
    awayId = game["gameData"]["teams"]["away"]["id"]
    homeTeam = getTeamName(homeId)
    awayTeam = getTeamName(awayId)
    return [homeTeam, awayTeam]

def getTeamName(teamId):
    team = statsapi.get('team', {'teamId': teamId})
    teamName = "null"
    teams = team['teams']
    for teamInfo in teams:
        if teamInfo['id'] == teamId:
            teamName = teamInfo['name']
    return teamName

# def printAllPitchesFromGame(game):
#     testOut = ""
#     awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
#     homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
#     currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
#     situation = Situation(homeAbbr, awayAbbr, currentPitcher)
#     lastDescription = ""
#     currentPlay = game["liveData"]["plays"]["currentPlay"]
#     plays = game["liveData"]["plays"]["allPlays"]
#     playIdx = 0
#     i = 0
#     while not situation.gameOver:
#         currentPlay = game["liveData"]["plays"]["currentPlay"]
#         currentPlay = plays[playIdx]
#         liveDescription = currentPlay["result"]["description"]
#         if (lastDescription != liveDescription):
#             lastDescription = liveDescription
#             situation.setInning(currentPlay["about"]["inning"])
#             situation.setTop(currentPlay["about"]["isTopInning"])
#             # situation.setOuts(currentPlay["count"]["outs"])
#             situation.setPitcher(currentPlay["matchup"]["pitcher"]["fullName"]) # José Quijada

#             # Loop through all play events of current play - print when a pitch is thrown
#             for index, playEvent in enumerate(currentPlay["playEvents"]):
#                 # Ignore if the event is not a pitch
#                 if not playEvent["isPitch"]:
#                     continue

#                 # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
#                 if index == len(currentPlay["playEvents"]) - 1:
#                     situation.setAwayScore(currentPlay["result"]["awayScore"])
#                     situation.setHomeScore(currentPlay["result"]["homeScore"])
#                     situation.setOuts(currentPlay["count"]["outs"])
#                     situation.setBalls(0)
#                     situation.setStrikes(0)
#                     basesOccupied = {1: False, 2: False, 3: False}
#                     if situation.outs < 3:
#                         if currentPlay["matchup"].get("postOnFirst"):
#                             basesOccupied[1] = True
#                         if currentPlay["matchup"].get("postOnSecond"):
#                             basesOccupied[2] = True
#                         if currentPlay["matchup"].get("postOnThird"):
#                             basesOccupied[3] = True
#                     situation.setBaserunners(basesOccupied)

#                 else:
#                     situation.setBalls(playEvent["count"]["balls"])
#                     situation.setStrikes(playEvent["count"]["strikes"])
#                     situation.setOuts(playEvent["count"]["outs"])

#                 # Incrememnt pitch count for current pitcher
#                 pitchCount = situation.pitchCount.get(situation.pitcher, 0)
#                 pitchCount += 1
#                 situation.pitchCount[situation.pitcher] = pitchCount

#                 print(f"{drawPitch(situation)}\n")
#                 if (situation.balls == 3 and situation.strikes == 2 and situation.outs == 2 and situation.awayScore == 0 and situation.homeScore == 3 and situation.inning == 9):
#                     testOut = drawPitch(situation)
#                 i += 1

#             # Check if the result of this at bat finished the game
#             if situation.inning >= 9:
#                 if situation.outs >= 3:
#                     if situation.top:
#                         if situation.homeScore > situation.awayScore:
#                             situation.gameOver = True
#                     else:
#                         if situation.homeScore != situation.awayScore:
#                             situation.gameOver = True
#                 else:
#                     if not situation.top and situation.homeScore > situation.awayScore:
#                         situation.gameOver = True
#         playIdx += 1

#     border = ""
#     recap = ""
#     if situation.awayScore > situation.homeScore:
#         recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
#     else:
#         recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
#     while len(border) < len(recap):
#         border += "─"
#     border = "+" + border[1:-1] + "+"
#     print()
#     print(border)
#     print(recap)
#     print(border)
#     return testOut

def printAllPitchesFromLiveGame(gamePk, output, stop_event):
    while not stop_event.is_set():
        game = statsapi.get('game', {'gamePk': gamePk})
        if game is None:
            print("Game is None")
            output.emit("Game is None")
            return
        awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
        homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
        currentPitcher = game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("matchup", {}).get("pitcher", {}).get("fullName", "N/A")
        situation = Situation(homeAbbr, awayAbbr, currentPitcher)
        lastDescription = ""
        currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
        plays = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A")
        if (len(plays) == 0):
            print("Game has not started yet!")
            output.emit("Game has not started yet!")
            return
        playIdx = 0
        i = 0
        lastPlayJson = currentPlay
        newPlay = False
        processOldPlay = False
        while not situation.gameOver:
            while ((playIdx >= len(plays) or newPlay) and lastPlayJson == currentPlay):
                if stop_event.wait(2):
                    break
                game = statsapi.get('game', {'gamePk': gamePk})
                awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
                homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
                currentPitcher = game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("matchup", {}).get("pitcher", {}).get("fullName", "N/A")
                situation = Situation(homeAbbr, awayAbbr, currentPitcher)
                lastDescription = ""
                currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
                plays = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A")
                if lastPlayJson != currentPlay:
                    newPlay = True

            #currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
            #currentPlay = plays[playIdx]
            if not newPlay:
                currentPlay = plays[playIdx]
                liveDescription = currentPlay.get("result", {}).get("description", "N/A")
                processOldPlay = (lastDescription != liveDescription)
            lastPlayJson = currentPlay
            if processOldPlay or newPlay:
                lastDescription = liveDescription
                situation.setInning(currentPlay.get("about", {}).get("inning", -1))
                situation.setTop(currentPlay.get("about", {}).get("isTopInning", False))
                # situation.setOuts(currentPlay["count"]["outs"])
                situation.setPitcher(currentPlay.get("matchup", {}).get("pitcher", {}).get("fullName", "N/A")) # José Quijada

                # Loop through all play events of current play - print when a pitch is thrown
                for index, playEvent in enumerate(currentPlay.get("playEvents", {})):
                    # Ignore if the event is not a pitch
                    if not playEvent.get("isPitch", False):
                        continue

                    # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
                    if index == len(currentPlay.get("playEvents", {})) - 1:
                        situation.setAwayScore(currentPlay.get("result", {}).get("awayScore", -1))
                        situation.setHomeScore(currentPlay.get("result", {}).get("homeScore", -1))
                        situation.setOuts(currentPlay.get("count", {}).get("outs", -1))
                        situation.setBalls(0)
                        situation.setStrikes(0)
                        basesOccupied = {1: False, 2: False, 3: False}
                        if situation.outs < 3:
                            if currentPlay.get("matchup", {}).get("postOnFirst", False):
                                basesOccupied[1] = True
                            if currentPlay.get("matchup", {}).get("postOnSecond", False):
                                basesOccupied[2] = True
                            if currentPlay.get("matchup", {}).get("postOnThird", False):
                                basesOccupied[3] = True
                        situation.setBaserunners(basesOccupied)

                    else:
                        situation.setBalls(playEvent.get("count", {}).get("balls", -1))
                        situation.setStrikes(playEvent.get("count", {}).get("strikes", -1))
                        situation.setOuts(playEvent.get("count", {}).get("outs", -1))

                    # Incrememnt pitch count for current pitcher
                    pitchCount = situation.pitchCount.get(situation.pitcher, 0)
                    pitchCount += 1
                    situation.pitchCount[situation.pitcher] = pitchCount

                    print(f"{drawPitch(situation)}")
                    output.emit(drawPitch(situation))
                    i += 1

                # Check if the result of this at bat finished the game
                if situation.inning >= 9:
                    if situation.outs >= 3:
                        if situation.top:
                            if situation.homeScore > situation.awayScore:
                                situation.gameOver = True
                        else:
                            if situation.homeScore != situation.awayScore:
                                situation.gameOver = True
                    else:
                        if not situation.top and situation.homeScore > situation.awayScore:
                            situation.gameOver = True
            playIdx += 1

        border = ""
        recap = ""
        if situation.awayScore > situation.homeScore:
            recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
        else:
            recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
        while len(border) < len(recap):
            border += "─"
        border = "+" + border[1:-1] + "+"
        print()
        print(border)
        print(recap)
        print(border)
        output.emit('\n')
        output.emit(border)
        output.emit(recap)
        output.emit(border)
        think = 0
        while (think < 6):
            output.emit("Steven is awesome")
            if stop_event.wait(1):
                break
            think += 1
        return

def main():
    '''
    +======================+
    |   Live Play Output   |
    +======================+
    '''
    # game = statsapi.get('game', {'gamePk': 776189})
    # # with open("meadows.json", "r") as f:
    # # # with open("example_out.json", "r") as f:
    # #     game = json.load(f)
    # pitchbypitch.printLiveGame(game)
    #printTeamName(116)
    
    #getTeamsByGame(776189)
    # gamePk = getGamePk()
    # if (gamePk == -1):
    #     print(f"The {desiredTeam} do not play today!")
    #     return 0

    # game = statsapi.get('game', {'gamePk': gamePk})
    gamePk = 823745
    printAllPitchesFromLiveGame(gamePk)
    return 0

if __name__ == "__main__":
    main()
