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
    output.emit(currentPlay.get("result", {}).get("description", "")) # print at bat description
    situation.setInning(currentPlay.get("about", {}).get("inning", -1))
    situation.setTop(currentPlay.get("about", {}).get("isTopInning", False))
    # situation.setOuts(currentPlay["count"]["outs"])
    situation.setPitcher(currentPlay.get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))

    # Loop through all play events of current play - print when a pitch is thrown
    for index, playEvent in enumerate(currentPlay.get("playEvents", {})):
        # Ignore if the event is not a pitch
        if not playEvent.get("isPitch", False):
            # update if a run scored mid at bat - wild pitch, stolen home, error on pick off, etc
            awayScore = playEvent.get("details", {}).get("awayScore", -1)
            if awayScore > -1:
                situation.setAwayScore(awayScore)
            homeScore = playEvent.get("details", {}).get("homeScore", -1)
            if homeScore > -1:
                situation.setHomeScore(homeScore)
            continue

        # TODO: Write logic for run being scored within an at bat (passed ball/wild pitch, for example) - written above. Test
        # Set score, baserunners, and outs (accounts for stolen bases, pick offs, etc)
        # We can see start base and end base in [runners][movement], and [runners][details][playIndex] shows when the change happens

        # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
        curIndex = len(currentPlay.get("playEvents", {})) - 1
        if index == curIndex or curIndex == -1:
            situation.setAwayScore(currentPlay.get("result", {}).get("awayScore", -1))
            situation.setHomeScore(currentPlay.get("result", {}).get("homeScore", -1))
            situation.setOuts(currentPlay.get("count", {}).get("outs", -1))
            situation.setBalls(0)
            situation.setStrikes(0)
            situation.setBaserunnersFromPlay(currentPlay, True)

        else:
            situation.setBalls(playEvent.get("count", {}).get("balls", -1))
            situation.setStrikes(playEvent.get("count", {}).get("strikes", -1))
            situation.setOuts(playEvent.get("count", {}).get("outs", -1))
            situation.setBaserunnersFromPlay(currentPlay, False)

        # Incrememnt pitch count for current pitcher
        pitchCount = situation.pitchCount.get(situation.pitcher, 0)
        pitchCount += 1
        situation.pitchCount[situation.pitcher] = pitchCount

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
        # with open("extra_innings_away_wins.json", "r") as f:
        #     game = json.load(f)
        if game is None:
            output.emit("Game is None")
            return
        awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
        homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
        situation = Situation()
        lastProcessedAtBatIndex = -1
        currentAtBat = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
        atBats = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A") # a play is an at bat from this game
        if (len(atBats) == 0):
            output.emit("Game has not started yet!")
            return
        atBatIndexToProcess = 0
        atBatToProcess = atBats[0]
        newAtBat = False
        processCachedAtBat = False
        situation.startNewGame(homeAbbr, awayAbbr, atBats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))
        while not situation.gameOver:
            # two situations:
            # the at bat is done and processed and the next at bat has not started yet (lastProcessedAtBatIndex == currentAtBatIndex or currentPlay[about][isComplete] is True)
            # the at bat is ongoing but not done yet, and we have already processed the last pitch (currentPlay[about][isComplete] is False and currentPlay[playEvents][-1][index] == last processed index)
            # TODO: Implement this correctly. This part should just wait for a new at bat.
            # TODO: Within an at bat, we wait for isComplete to be True, and if it isn't then we continue to ping from within.
            while ((atBatIndexToProcess >= len(atBats) or newAtBat) and
                    lastProcessedAtBatIndex == currentAtBatIndex):
                if stop_event.wait(2):
                    break
                game = statsapi.get('game', {'gamePk': gamePk})
                currentAtBat = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
                currentAtBatIndex = currentAtBat.get("about", {}).get("atBatIndex", -1)
                atBats = game.get("liveData", {}).get("plays", {}).get("allPlays", "N/A")
                # This is a new at bat - process it
                if lastProcessedAtBatIndex != currentAtBatIndex:
                    atBatToProcess = currentAtBat
                    newAtBat = True

            #currentPlay = game.get("liveData", {}).get("plays", {}).get("currentPlay", "N/A")
            #currentPlay = plays[playIdx]
            # We are processing previously cached at bats until live IRL
            if not newAtBat:
                currentAtBat = atBats[atBatIndexToProcess]
                currentAtBatIndex = currentAtBat.get("about", {}).get("atBatIndex", -1)
                if lastProcessedAtBatIndex != currentAtBatIndex:
                    processCachedAtBat = True
                    atBatToProcess = currentAtBat
            if processCachedAtBat or newAtBat:
                processAtBat(situation, atBatToProcess, output)
                lastProcessedAtBatIndex = currentAtBatIndex
                atBatIndexToProcess += 1

        border = ""
        recap = ""
        if situation.awayScore > situation.homeScore:
            recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
        else:
            recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
        while len(border) < len(recap):
            border += "─"
        border = "+" + border[1:-1] + "+"
        output.emit("")
        output.emit(border)
        output.emit(recap)
        output.emit(border)
        threadTest = 0
        while (threadTest < 6):
            output.emit("Steven is awesome")
            if stop_event.wait(1):
                break
            threadTest += 1
        return

def outputVerbosePrinting(text):
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
    testThread.output.connect(outputVerbosePrinting)
    printAllPitchesFromLiveGame(gamePk, testThread.output, testThread.stop_event)
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
