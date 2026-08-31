import json
import requests
import statsapi
import time
from enum import Enum
from print_util import dprint
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
            dprint(status)
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

    def __str__(self):
        return f"{self.game}\ngamePK: {self.gamePk}\nsituation: {self.situation}"
