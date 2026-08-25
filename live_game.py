from application_util import *
import json
import statsapi
import sys
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

def pingUntilNextPitch():
    return False

def processAtBat(situation, currentPlay, output):
    vprint("New at bat. Index: ", currentPlay.get("atBatIndex", -1)) # verbose log. FIXME: remove
    situation.setInning(currentPlay.get("about", {}).get("inning", -1))
    situation.setTop(currentPlay.get("about", {}).get("isTopInning", False))
    # situation.setOuts(currentPlay["count"]["outs"])
    situation.setPitcher(currentPlay.get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))

    # Loop through all play events of current play - print when a pitch is thrown
    for index, playEvent in enumerate(currentPlay.get("playEvents", {})):
        # Ignore if the event is not a pitch
        if not playEvent.get("isPitch", False):
            continue

        # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
        curIndex = len(currentPlay.get("playEvents", {})) - 1
        if index == curIndex or curIndex == -1:
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

        # vprint(f"{drawPitch(situation)}")
        # output.emit(currentPlay["result"]["description"])
        output.emit(drawPitch(situation))

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

def printAllPitchesFromLiveGame(gamePk, output, stop_event):
    while not stop_event.is_set():
        game = statsapi.get('game', {'gamePk': gamePk})
        # with open("example_game.json", "r") as f:
        #     game = json.load(f)
        if game is None:
            # vprint("Game is None")
            output.emit("Game is None")
            return
        awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
        homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
        currentPitcher = game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("matchup", {}).get("pitcher", {}).get("fullName", "N/A")
        situation = Situation()
        lastAtBatIndex = -1
        currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
        plays = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A")
        if (len(plays) == 0):
            # vprint("Game has not started yet!")
            output.emit("Game has not started yet!")
            return
        playIdx = 0
        i = 0
        lastPlayJson = currentPlay
        newPlay = False
        processCachedPlay = False
        # Print the situation before the game's first pitch
        situation.startNewGame(homeAbbr, awayAbbr, plays[0].get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))
        output.emit(drawPitch(situation))
        while not situation.gameOver:
            # two situations:
            # the at bat is done and processed and the next at bat has not started yet (lastAtBatIndex == currentAtBatIndex or currentPlay[about][isComplete] is True)
            # the at bat is ongoing but not done yet, and we have already processed the last pitch (currentPlay[about][isComplete] is False and currentPlay[playEvents][-1][index] == last processed index)
            while ((playIdx >= len(plays) or newPlay) and
                    lastPlayJson == currentPlay):
                if stop_event.wait(2):
                    break
                game = statsapi.get('game', {'gamePk': gamePk})
                awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
                homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
                currentPitcher = game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("matchup", {}).get("pitcher", {}).get("fullName", "N/A")
                #situation = Situation(homeAbbr, awayAbbr, currentPitcher)
                lastAtBatIndex = -1
                currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
                plays = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A")
                if lastPlayJson != currentPlay:
                    newPlay = True

            #currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
            #currentPlay = plays[playIdx]
            if not newPlay:
                currentPlay = plays[playIdx]
                currentAtBatIndex = currentPlay.get("about", {}).get("atBatIndex", -1)
                processCachedPlay = (lastAtBatIndex != currentAtBatIndex)
            lastPlayJson = currentPlay
            if processCachedPlay or newPlay:
                lastAtBatIndex = currentAtBatIndex
                processAtBat(situation, currentPlay, output)
                i += 1
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
        # vprint()
        # vprint(border)
        # vprint(recap)
        # vprint(border)
        output.emit("")
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

def outputTesting(text):
    vprint(text)

def main(args):
    '''
    +======================+
    |   Live Play Output   |
    +======================+
    '''
    getOptions(args)

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
    testThread = LiveGameWorker(gamePk)
    testThread.output.connect(outputTesting)
    printAllPitchesFromLiveGame(gamePk, testThread.output, testThread.stop_event)
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
