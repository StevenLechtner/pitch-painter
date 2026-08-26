import application_util
import json
from print_util import vprint
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

def processPlayEvent(playEvent, situation, atBatToProcess, output):
    # Ignore if the event is not a pitch
    if not playEvent.get("isPitch", False):
        # update if a run scored mid at bat - wild pitch, stolen home, error on pick off, etc
        awayScore = playEvent.get("details", {}).get("awayScore", -1)
        if awayScore > -1:
            situation.setAwayScore(awayScore)
        homeScore = playEvent.get("details", {}).get("homeScore", -1)
        if homeScore > -1:
            situation.setHomeScore(homeScore)
        return

    print("Is current play complete? ", atBatToProcess.get("about", {}).get("isComplete", False))
    print("Current playEvents[-1] index", atBatToProcess.get("playEvents", {})[-1].get("index", -1))
    print("Current playEvent index", playEvent.get("index", -1))
    if atBatToProcess.get("about", {}).get("isComplete", False) and \
        (atBatToProcess.get("playEvents", {})[-1].get("index", -1) == playEvent.get("index", -1)):
        # The at bat is complete - set score, baserunners, and outs, and set balls and strikes to 0
        situation.setAwayScore(atBatToProcess.get("result", {}).get("awayScore", -1))
        situation.setHomeScore(atBatToProcess.get("result", {}).get("homeScore", -1))
        situation.setOuts(atBatToProcess.get("count", {}).get("outs", -1))
        situation.setBalls(0)
        situation.setStrikes(0)
        situation.setBaserunnersFromPlay(atBatToProcess, True)
    else:
        # Pitch was thrown - set current count and baserunners
        situation.setBalls(playEvent.get("count", {}).get("balls", -1))
        situation.setStrikes(playEvent.get("count", {}).get("strikes", -1))
        situation.setOuts(playEvent.get("count", {}).get("outs", -1))
        situation.setBaserunnersFromPlay(atBatToProcess, False)

    # Incrememnt pitch count for current pitcher
    pitchCount = situation.pitchCount.get(situation.pitcher, 0)
    pitchCount += 1
    situation.pitchCount[situation.pitcher] = pitchCount

    output.emit(drawPitch(situation))

def processAtBat(situation, atBatToProcess, atBatIndexToProcess, output, gamePk, stop_event):
    vprint("New at bat. Index: ", atBatToProcess.get("atBatIndex", -1)) # verbose log. FIXME: remove
    output.emit(atBatToProcess.get("result", {}).get("description", "")) # print at bat description
    situation.setInning(atBatToProcess.get("about", {}).get("inning", -1))
    situation.setTop(atBatToProcess.get("about", {}).get("isTopInning", False))
    # situation.setOuts(currentPlay["count"]["outs"])
    situation.setPitcher(atBatToProcess.get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))

    # Loop through all play events of current play - print when a pitch is thrown
    latestPlayEventIndex = -1
    currentPlayEventToProcess = 0
    playEvents = atBatToProcess.get("playEvents", [])

    # First process all pitches from currentPlay
    for playEvent in playEvents:
        processPlayEvent(playEvent, situation, atBatToProcess, output)
        currentPlayEventToProcess += 1
    # Then check if the at bat is complete
    if not atBatToProcess.get("about", {}).get("isComplete", False):
        # If it's not, then wait for it to be complete
        # TODO: Check this works during a live game!
        while not atBatToProcess.get("about", {}).get("isComplete", False) or currentPlayEventToProcess <= latestPlayEventIndex:
            while currentPlayEventToProcess <= latestPlayEventIndex:
                processPlayEvent(playEvents[currentPlayEventToProcess], situation, atBatToProcess, output)
                currentPlayEventToProcess += 1
            # Ping until a new pitch is thrown
            if stop_event.wait(2):
                break
            game = statsapi.get('game', {'gamePk': gamePk})
            atBats = game.get("liveData", {}).get("plays", {}).get("allPlays", [])
            if atBats:
                latestAtBatIndex = atBats[-1].get("atBatIndex", -1)
            else:
                print("atBats len is 0. TODO: Check why...")
                latestAtBatIndex = -1
                continue
            print("atBatIndexToProcess: ", atBatIndexToProcess)
            print("latestAtBatIndex: ", latestAtBatIndex)
            if atBatIndexToProcess <= latestAtBatIndex:
                atBatToProcess = atBats[atBatIndexToProcess]
                playEvents = atBatToProcess.get("playEvents", [])
                latestPlayEventIndex = playEvents[-1].get("index", -1) if playEvents else -1

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
        # with open("ghost_runner_worked_somehow.json", "r") as f:
        #     game = json.load(f)
        if game is None:
            output.emit("Game is None")
            return
        awayAbbr = game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
        homeAbbr = game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
        situation = Situation()
        atBats = game.get("liveData", {}).get("plays", {}).get("allPlays", []) # a play is an at bat from this game
        if (len(atBats) == 0):
            output.emit("Game has not started yet!")
            return
        atBatIndexToProcess = 0
        # for atBat in atBats:
        #     print(f"{atBat.get("atBatIndex", -1)} - {atBat.get("about", {}).get("isComplete", False)}")
        # return
        
        situation.startNewGame(homeAbbr, awayAbbr, atBats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))
        while not situation.gameOver:
            if atBats:
                latestAtBatIndex = atBats[-1].get("atBatIndex", -1)
            else:
                latestAtBatIndex = -1
            # All at bats have been processed but the game is not over - ping and wait for next at bat from the server
            while atBatIndexToProcess > latestAtBatIndex:
                print("Waiting for next at bat to start...")
                if stop_event.wait(2):
                    break
                game = statsapi.get('game', {'gamePk': gamePk})
                #currentAtBat = game.get("liveData", {}).get("plays", {}).get("currentPlay", {})
                #currentAtBatIndex = currentAtBat.get("atBatIndex", -1)
                atBats = game.get("liveData", {}).get("plays", {}).get("allPlays", [])
                if atBats:
                    latestAtBatIndex = atBats[-1].get("atBatIndex", -1)
                else:
                    print("atBats len is 0. TODO: Check why...")
                    latestAtBatIndex = -1
                    continue

            # Right here we know that atBatIndexToProcess is <= latestAtBatIndex
            # We want to get atBatIndexToProcess to be > latestAtBatIndex
            # Processing an at bat from atBats[atBatIndexToProcess] increments atBatIndexToProcess
            # Rinse and repeat until atBatIndexToProcess > latestAtBatIndex

            # We process the next at bat at atBatIndexToProcess
            print("atBatIndexToProcess", atBatIndexToProcess)
            print("latestAtBatIndex", latestAtBatIndex)
            processAtBat(situation, atBats[atBatIndexToProcess], atBatIndexToProcess, output, gamePk, stop_event)
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
    application_util.getOptions(args)

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
    gamePk = 823989
    testThread = application_util.LiveGameWorker(gamePk)
    testThread.output.connect(outputVerbosePrinting)
    printAllPitchesFromLiveGame(gamePk, testThread.output, testThread.stop_event)
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
