import cli
import datetime
import json
import statsapi
import sys
import threading
import time
import win_probability
from game import Game, Status
from pitchbypitch import drawPitch, postPitchToThreads
from print_util import vprint, dprint
from PySide6 import QtCore

desiredTeam = 'Detroit Tigers'

class LiveGameWorker(QtCore.QObject):
    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self, gamePk):
        super().__init__()
        self.gamePk = gamePk
        self.stop_event = threading.Event()

    @QtCore.Slot()
    def run(self):
        printAllPitchesFromLiveGame(self.gamePk, self.output, self.stop_event)
        self.finished.emit()

    def stop(self):
        self.stop_event.set()

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

def isABigPlay(playEvent, atBatToProcess, game):
    if atBatToProcess.get("about", {}).get("isComplete", False) and \
        (atBatToProcess.get("playEvents", {})[-1].get("index", -1) == playEvent.get("index", -1)):
        winProb = win_probability.WinProbability(game.gamePk)
        return winProb.isAboveThreshold(atBatToProcess.get("about", {}).get("atBatIndex", -1))
    return False

def processPlayEvent(playEvent, situation, atBatToProcess, game, output):
    # now = datetime.datetime.now()
    # curTime = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
    playEndTime = playEvent.get("endTime", -1).replace(":", "-").replace("T", "_").replace("Z", "")
    situation.setPlayEventId(playEvent.get("playId", f"play_end_time_{playEndTime}"))
    game.setLastPitch(situation)

    if playEvent.get("isPitch", False):
        output.emit(drawPitch(situation))

        # TODO: implement this as another flag - printing every pitch in the game (remove big play stuff...)
        # playId = playEvent.get("playId", -1)
        # filepath = f"images/{game.gamePk}/{playId}.png"
        # #if (atBatToProcess.get("atBatIndex", -1) >= 65):
        # if cli.threading:
        #     if game.isLive():
        #         print("game is live")
        #         curIdx = game.game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("about", {}).get("atBatIndex", -1)
        #         thisBatIdx = atBatToProcess.get("about", {}).get("atBatIndex", -1)
        #         print(curIdx)
        #         print(thisBatIdx)
        #         if curIdx == thisBatIdx and curIdx != -1:
        #             if isABigPlay(playEvent, atBatToProcess, game):
        #                 description = atBatToProcess.get("result", {}).get("description", "")
        #                 postPitchToThreads(situation, filepath, description=description)
        #     else:
        #         if isABigPlay(playEvent, atBatToProcess, game):
        #             description = atBatToProcess.get("result", {}).get("description", "")
        #             postPitchToThreads(situation, filepath, description=description)
        # else:
        #     vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")

    # update if a run scored mid at bat - wild pitch, stolen home, error on pick off, etc
    scoringPlay = playEvent.get("details", {}).get("isScoringPlay", False)
    awayScore = playEvent.get("details", {}).get("awayScore", -1)
    if awayScore > -1:
        situation.setAwayScore(awayScore)
    homeScore = playEvent.get("details", {}).get("homeScore", -1)
    if homeScore > -1:
        situation.setHomeScore(homeScore)
    if scoringPlay:
        now = datetime.datetime.now()
        curTime = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
        filepath = f"images/{game.gamePk}/play_id_{game.lastPitch.playEventId}_created_{curTime}.png"
        description = playEvent.get("details", {}).get("description", "")
        postPitchToThreads(game.lastPitch, filepath, description=description, scoringPlay=True, awayScore=situation.awayScore, homeScore=situation.homeScore)
    # set pitcher for every play event and update pitcher if play event type is a pitching_substitution
    game.setPitcher(playEvent)

    dprint("Is current play complete? ", atBatToProcess.get("about", {}).get("isComplete", False))
    dprint("Current playEvents[-1] index", atBatToProcess.get("playEvents", {})[-1].get("index", -1))
    dprint("Current playEvent index", playEvent.get("index", -1))
    if atBatToProcess.get("about", {}).get("isComplete", False) and \
        (atBatToProcess.get("playEvents", {})[-1].get("index", -1) == playEvent.get("index", -1)):
        # The at bat is complete - set score, baserunners, and outs, and set balls and strikes to 0
        situation.setAwayScore(atBatToProcess.get("result", {}).get("awayScore", -1))
        situation.setHomeScore(atBatToProcess.get("result", {}).get("homeScore", -1))
        situation.setOuts(atBatToProcess.get("count", {}).get("outs", -1))
        situation.setBalls(0)
        situation.setStrikes(0)
        situation.setBaserunnersAtEndOfAtBat(atBatToProcess)
    else:
        # Pitch was thrown - set current count and baserunners
        situation.setBalls(playEvent.get("count", {}).get("balls", -1))
        situation.setStrikes(playEvent.get("count", {}).get("strikes", -1))
        situation.setOuts(playEvent.get("count", {}).get("outs", -1))
        situation.setBaserunnersDuringAtBat(atBatToProcess, playEvent.get("index", -1))

    # Incrememnt pitch count for current pitcher
    if playEvent.get("isPitch", False):
        pitchCount = game.pitchCountDict.get(situation.pitcher, 0)
        pitchCount += 1
        game.pitchCountDict[situation.pitcher] = pitchCount
        situation.setPitchCount(pitchCount)
    # ANOTHER WAY - issue with this is that the pitch count only works if this pitch to process is the latest pitch (live):
    # ["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["id"]
    # ["liveData"]["boxscore"]["teams"]["away"]["players"]["ID676282"]["person"]["id"]
    # ["liveData"]["boxscore"]["teams"]["away"]["players"]["ID676282"]["stats"]["numberOfPitches"]

# TODO: Pitching change during an inning does not update until the second at bat happens - should check pitcher every pitch honestly
def processAtBat(game, atBatIndexToProcess, output, gamePk, stop_event):
    situation = game.situation
    atBatToProcess = game.atBats[atBatIndexToProcess]
    dprint("New at bat. Index: ", atBatToProcess.get("atBatIndex", -1))
    dprint(f"Now batting: {atBatToProcess.get("matchup", {}).get("batter", {}).get("fullName", "")}")
    situation.setInning(atBatToProcess.get("about", {}).get("inning", -1))
    situation.setTop(atBatToProcess.get("about", {}).get("isTopInning", False))
    game.setPitcher() # set pitcher when new at bat starts to account for inning change
    situation.setBaserunnersAtStartOfAtBat(atBatToProcess)

    # Loop through all play events of current play - print when a pitch is thrown
    latestPlayEventIndex = -1
    currentPlayEventToProcess = 0
    playEvents = atBatToProcess.get("playEvents", [])

    # First process all pitches from currentPlay
    for playEvent in playEvents:
        processPlayEvent(playEvent, situation, atBatToProcess, game, output)
        currentPlayEventToProcess += 1
    # Then check if the at bat is complete
    if not atBatToProcess.get("about", {}).get("isComplete", False):
        # If it's not, then wait for it to be complete
        while not atBatToProcess.get("about", {}).get("isComplete", False) or currentPlayEventToProcess <= latestPlayEventIndex:
            while currentPlayEventToProcess <= latestPlayEventIndex:
                processPlayEvent(playEvents[currentPlayEventToProcess], situation, atBatToProcess, game, output)
                currentPlayEventToProcess += 1
            # Ping until a new pitch is thrown
            dprint("Waiting for the next pitch of the at bat...")
            if stop_event.wait(2):
                return
            game.getGameByGamePk(gamePk)
            atBats = game.game.get("liveData", {}).get("plays", {}).get("allPlays", [])
            if atBats:
                latestAtBatIndex = atBats[-1].get("atBatIndex", -1)
            else:
                dprint("atBats len is 0. TODO: Check why...")
                latestAtBatIndex = -1
                continue
            dprint("atBatIndexToProcess: ", atBatIndexToProcess)
            dprint("latestAtBatIndex: ", latestAtBatIndex)
            if atBatIndexToProcess <= latestAtBatIndex:
                atBatToProcess = atBats[atBatIndexToProcess]
                playEvents = atBatToProcess.get("playEvents", [])
                latestPlayEventIndex = playEvents[-1].get("index", -1) if playEvents else -1

    game.processAtBatFinished(atBatToProcess)

def printAllPitchesFromLiveGame(gamePk, output, stop_event):
    while not stop_event.is_set():
        game = Game()
        game.getGameByGamePk(gamePk)
        # game.getGameByFilePath("tests/meadows.json") # Uncomment to test from a json file instead of the server
        game.setStatus()
        if not game.isValid() or game.gameStatus == Status.PREVIEW:
            output.emit(game.gameInfo)
            return

        atBatIndexToProcess = 0
        while not game.situation.gameOver and not stop_event.is_set():
            if game.atBats:
                latestAtBatIndex = game.atBats[-1].get("atBatIndex", -1)
            else:
                latestAtBatIndex = -1
            while atBatIndexToProcess > latestAtBatIndex:
                # All at bats have been processed but the game is not over - ping and wait for next at bat from the server
                dprint("Waiting for next at bat to start...")
                if stop_event.wait(2):
                    return # stop_event was sent, return
                game.getGameByGamePk(gamePk)
                if game.atBats:
                    latestAtBatIndex = game.atBats[-1].get("atBatIndex", -1)
                else:
                    dprint("atBats len is 0. TODO: Check why...")
                    latestAtBatIndex = -1
                    continue

            # Right here we know that atBatIndexToProcess is <= latestAtBatIndex
            # We process the next at bat at atBatIndexToProcess
            dprint("atBatIndexToProcess", atBatIndexToProcess)
            dprint("latestAtBatIndex", latestAtBatIndex)
            processAtBat(game, atBatIndexToProcess, output, gamePk, stop_event)
            vprint(game.atBats[atBatIndexToProcess].get("result", {}).get("description", "")) # print at bat description
            atBatIndexToProcess += 1

        # additional check - stop_event got set within processAtBat()
        if stop_event.is_set():
            return

        border = ""
        recap = game.getRecap()
        while len(border) < len(recap):
            border += "─"
        border = "+" + border[1:-1] + "+"
        output.emit("")
        output.emit(border)
        output.emit(recap)
        output.emit(border)
        threadTest = 0
        while (threadTest < 6):
            vprint(f"Testing thread/stop_event ({threadTest + 1}/6)")
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
    cli.getOptions(args)

    # game = statsapi.get('game', {'gamePk': 776189})
    # # with open("tests/meadows.json", "r") as f:
    # # # with open("tests/example_out.json", "r") as f:
    # #     game = json.load(f)
    # pitchbypitch.printLiveGame(game)
    #printTeamName(116)

    #getTeamsByGame(776189)
    # gamePk = getGamePk()
    # if (gamePk == -1):
    #     print(f"The {desiredTeam} do not play today!")
    #     return 0

    # game = statsapi.get('game', {'gamePk': gamePk})
    # gamePk = 823989
    # gamePk = 745369
    gamePk = 822765
    testThread = LiveGameWorker(gamePk)
    testThread.output.connect(outputVerbosePrinting)
    printAllPitchesFromLiveGame(gamePk, testThread.output, testThread.stop_event)
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
