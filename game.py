import json
import requests
import statsapi
import time
from situation import Situation

class Game():
    def __init__(self):
        self.game = None
        self.gamePk = -1
        self.situation = Situation()

    def startNewGame(self):
        awayAbbr = self.game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "N/A")
        homeAbbr = self.game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "N/A")
        atBats = self.game.get("liveData", {}).get("plays", {}).get("allPlays", []) # a play is an at bat from this game
        self.situation = Situation()
        self.situation.startNewGame(homeAbbr, awayAbbr, atBats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "N/A"))

    # TODO: Instead of start new game every time, just set the away team name, home team name, and whatever else?
    def getGameByGamePk(self, _gamePk):
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            try:
                self.game = statsapi.get('game', {'gamePk': _gamePk})
                self.gamePk = _gamePk
                self.startNewGame()
                return self.game
            except requests.exceptions.RequestException as e:
                print(f"https://statsapi.mlb.com/api/v1.1/game/{_gamePk}/feed/live request failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(1)

        print("Failed to retrieve game GET request after 3 attempts.")
        self.game = None
        self.gamePk = -1
        self.situation = Situation()
        return None
    
    def getGameByFilePath(self, _filePath):
        with open(_filePath, "r") as f:
            self.game = json.load(f)
        self.startNewGame()

    def getRecap(self):
        if self.situation.awayScore > self.situation.homeScore:
            return f"|  Final score: {self.situation.awayScore}-{self.situation.homeScore}, {self.situation.awayTeam} over {self.situation.homeTeam}  |"
        else:
            return f"|  Final score: {self.situation.homeScore}-{self.situation.awayScore}, {self.situation.homeTeam} over {self.situation.awayTeam}  |"

    def __str__(self):
        return f"{self.game}\ngamePK: {self.gamePk}\nsituation: {self.situation}"
