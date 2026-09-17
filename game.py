import cli
import copy
import json
import requests
import statsapi
import time
import win_probability
from enum import Enum
from pitchbypitch import postPitchToThreads
from print_util import dprint, vprint
from situation import Situation

class Status(Enum):
    PREVIEW = 1
    LIVE = 2
    FINAL = 3
    UNKNOWN = 4

class Game():
    def __init__(self):
        self.game = None
        self.gamePk = -1
        self.situation = Situation()
        self.lastPitch = Situation()
        self.gameInfo = ""
        self.atBats = None
        self.curAwayPitcher = ""
        self.curHomePitcher = ""
        self.curPitcher = ""
        self.gameStatus = Status.UNKNOWN
        self.detailedState = ""
    """
        if game.game is None:
            output.emit("Game is None")
            return
        atBats = game.game.get("liveData", {}).get("plays", {}).get("allPlays", []) # a play is an at bat from this game
        if (len(atBats) == 0):
            output.emit("Game has not started yet!")
            return
    """

    def isValid(self):
        if self.game is None:
            dprint("Game is nothing for some reason")
            self.gameInfo = "Game is None"
            return False
        self.atBats = self.game.get("liveData", {}).get("plays", {}).get("allPlays", []) # a play is an at bat from this game
        if (len(self.atBats) == 0):
            dprint("Game has not started yet!")
            return False
        return True
    
    def setStatus(self):
        if self.game is not None:
            status = self.game.get("gameData", {}).get("status", {}).get("codedGameState", "")
            self.detailedState = self.game.get("gameData", {}).get("status", {}).get("detailedState", "")
            match status:
                case "P" | "S" | "U":
                    self.gameStatus = Status.PREVIEW
                    self.gameInfo = f"{self.detailedState}\nGame has not started yet!"
                case "I" | "M" | "E" | "C" | "D":
                    self.gameStatus = Status.LIVE
                    self.gameInfo = f"{self.detailedState}\nGame in progress!"
                case "F" | "O" | "W" | "A" | "D" | "T" | "R":
                    self.gameStatus = Status.FINAL
                    self.gameInfo = f"{self.detailedState}\nGame has ended!"
                case _:
                    self.gameStatus = Status.UNKNOWN
                    self.gameInfo = "Game status unknown!"
            dprint(f"Game status: {self.gameStatus} ({status})")

    def isLive(self):
        self.setStatus()
        return self.isValid() and self.gameStatus == Status.LIVE

    def startNewGame(self):
        if not self.isValid():
            return
        awayAbbr = self.game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "[away_team]")
        homeAbbr = self.game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "[home_team]")
        self.curAwayPitcher = self.game.get("gameData", {}).get("probablePitchers", {}).get("away", {}).get("fullName", "[away_pitcher]")
        self.atBats = self.game.get("liveData", {}).get("plays", {}).get("allPlays", []) # a play is an at bat from this game
        self.curHomePitcher = self.atBats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "[home_pitcher]")
        self.curPitcher = self.curHomePitcher
        self.situation = Situation()
        self.situation.startNewGame(homeAbbr, awayAbbr, self.curPitcher)

    # TODO: Test network connection failure
    def getGameByGamePk(self, _gamePk):
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            try:
                self.game = statsapi.get('game', {'gamePk': _gamePk})
                if not self.isValid():
                    continue # game we got was not valid, try again...
                if self.gamePk != _gamePk:
                    self.startNewGame()
                    self.gamePk = _gamePk
                return self.game
            except requests.exceptions.RequestException as e:
                print(f"https://statsapi.mlb.com/api/v1.1/game/{_gamePk}/feed/live request failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    print(f"Failed to retrieve game (game_pk={_gamePk}) GET request after 3 attempts.")
        return None
    
    def getGameByFilePath(self, _filePath):
        with open(_filePath, "r") as f:
            self.game = json.load(f)
        if self.gamePk != self.game.get("gamePk", -1):
            self.startNewGame()
            self.gamePk = self.game.get("gamePk", -1)

    def getRecap(self):
        if self.situation.awayScore > self.situation.homeScore:
            return f"|  Final score: {self.situation.awayScore}-{self.situation.homeScore}, {self.situation.awayTeam} over {self.situation.homeTeam}  |"
        else:
            return f"|  Final score: {self.situation.homeScore}-{self.situation.awayScore}, {self.situation.homeTeam} over {self.situation.awayTeam}  |"
        

    # sets current pitcher. Updates pitcher if play event type is a pitching_substitution
    def setPitcher(self, playEvent=None):
        if not self.isValid():
            return
        
        if playEvent is None:
            if self.situation.top:
                self.curPitcher = self.curHomePitcher
            else:
                self.curPitcher = self.curAwayPitcher
            self.situation.setPitcher(self.curPitcher)
            return
        
        default = "[home_pitcher]" if self.situation.top else "[away_pitcher]"
        pitcher = default
        if playEvent.get("details", {}).get("eventType", "") == "pitching_substitution":
            playerId = playEvent.get("player", {}).get("id", -1)
            pitcher = self.game.get("gameData", {}).get("players", {}).get(f"ID{playerId}", {}).get("fullName", default)
            if self.situation.top:
                self.curHomePitcher = pitcher
            else:
                self.curAwayPitcher = pitcher
        self.setPitcher()

    def setLastPitch(self, situation: Situation):
        self.lastPitch = copy.copy(situation)

    def processAtBatFinished(self, atBatToProcess):
        vprint("Processing at bat finished...")
        self.situation.setAwayScore(atBatToProcess.get("result", {}).get("awayScore", -1))
        self.situation.setHomeScore(atBatToProcess.get("result", {}).get("homeScore", -1))
        self.situation.setOuts(atBatToProcess.get("count", {}).get("outs", -1))
        self.situation.setBalls(0)
        self.situation.setStrikes(0)
        self.situation.setBaserunnersAtEndOfAtBat(atBatToProcess)
        # Check if the result of this at bat finished the game
        if self.situation.inning >= 9:
            if self.situation.outs >= 3:
                if self.situation.top:
                    if self.situation.homeScore > self.situation.awayScore:
                        self.situation.gameOver = True
                else:
                    if self.situation.homeScore != self.situation.awayScore:
                        self.situation.gameOver = True
            else:
                if not self.situation.top and self.situation.homeScore > self.situation.awayScore:
                    self.situation.gameOver = True
        # Half inning is over but game is not done yet - set outs to 0
        if not self.situation.gameOver and self.situation.outs == 3:
            self.situation.setOuts(0)

        # Post last pitch of at bat to threads if it's a big play
        if cli.threading:
            # Uncomment to skip posting until at or beyond a specific at bat (debugging purposes)
            # if (atBatToProcess.get("atBatIndex", -1) < 1000):
            #     vprint("At bat processed!")
            #     return
            filepath = f"images/{self.gamePk}/{self.lastPitch.playEventId}.png"

            # # Uncomment below to post all big plays of a game, even if the game is live - retroactively post big pitches form earlier in the game
            # # TODO: make this a flag
            winProb = win_probability.WinProbability(self.gamePk)
            if winProb.isABigPlay(atBatToProcess.get("about", {}).get("atBatIndex", -1)):
                description = atBatToProcess.get("result", {}).get("description", "")
                postPitchToThreads(self.lastPitch, filepath, description=description)

            # # Uncomment below to post live game pitches when actually live - don't retroactively post big pitches from earlier in the game
            # # TODO: make this a flag
            # curIdx = -1
            # thisBatIdx = -1
            # if self.isLive():
            #     dprint("game is live")
            #     curIdx = self.game.get("liveData", {}).get("plays", {}).get("currentPlay", {}).get("about", {}).get("atBatIndex", -1)
            #     thisBatIdx = atBatToProcess.get("about", {}).get("atBatIndex", -1)
            #     dprint(f"curIdx: {curIdx}")
            #     dprint(f"thisBatIdx: {thisBatIdx}")
            # if not self.isLive() or (self.isLive() and curIdx == thisBatIdx and curIdx != -1):
            #     if self.isABigPlay(atBatToProcess.get("about", {}).get("atBatIndex", -1)):
            #         description = atBatToProcess.get("result", {}).get("description", "")
            #         postPitchToThreads(self.lastPitch, filepath, description=description)
        else:
            vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")

        vprint("At bat processed!")

    def __str__(self):
        return f"{self.game}\ngamePK: {self.gamePk}\nsituation: {self.situation}"
