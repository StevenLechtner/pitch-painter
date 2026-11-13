"""
Game Class provides details about a real MLB baseball game. Status Enum specifies game state.

Functionality defines a game:
situation, at bats, pitchers, game state
"""


import pitchpainter.cli as cli
import copy
import json
import pitchpainter.pitch_posting_processor as pitch_posting_processor
import requests
import statsapi
import time
from enum import Enum
from pitchpainter.print_util import dprint, vprint
from pitchpainter.situation import Situation


class Status(Enum):
    """MLB game states, enum."""

    PREVIEW = 1
    LIVE = 2
    FINAL = 3
    UNKNOWN = 4


class Game():
    """Outlines important actions to parse a baseball game."""

    def __init__(self):
        """Initialize a game with empty contents."""
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
        self.pitchCountDict = {}
        self.gameOver = False

    def isValid(self):
        """Return True if the game is populated and has at least one at bat. False otherwise."""
        if self.game is None:
            dprint("Game is nothing for some reason")
            self.gameInfo = "Game is None"
            return False
        self.atBats = (
            self.game.get("liveData", {})
            .get("plays", {})
            .get("allPlays", [])
        )  # a play is an at bat from this game
        if (len(self.atBats) == 0):
            dprint("Game has not started yet!")
            return False
        return True

    def setStatus(self):
        """Set Game status from the game's codedGameState. UNKNOWN if codedGameState can not be found."""
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
        else:
            self.gameStatus = Status.UNKNOWN
            self.gameInfo = "Game status unknown; game attribute is None!"
        dprint(f"Game status: {self.gameStatus} ({status})")

    def isLive(self):
        """Grab Game status, an return True is Game is valid and has a status of LIVE. False otherwise."""
        self.setStatus()
        return self.isValid() and self.gameStatus == Status.LIVE

    def startNewGame(self):
        """Set up the object for a new game. Populate teams, set pitcher, start the first at bat."""
        if not self.isValid():
            return
        awayAbbr = self.game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "[away_team]")
        homeAbbr = self.game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "[home_team]")
        self.curAwayPitcher = (
            self.game.get("gameData", {})
            .get("probablePitchers", {})
            .get("away", {})
            .get("fullName", "[away_pitcher]")
        )
        self.atBats = (
            self.game.get("liveData", {})
            .get("plays", {})
            .get("allPlays", [])
        )  # a play is an at bat from this game
        self.curHomePitcher = self.atBats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "[home_pitcher]")
        self.curPitcher = self.curHomePitcher
        self.situation = Situation()
        self.situation.startNewGame(homeAbbr, awayAbbr, self.curPitcher)

    # TODO: Test network connection failure
    def getGameByGamePk(self, _gamePk):
        """Get game from MLB's server by gamePK.

        Attempt to gather data up to three times.
        Save, start, and return game if valid.
        Return None if game can not be found.
        """
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            try:
                self.game = statsapi.get('game', {'gamePk': _gamePk})
                if not self.isValid():
                    continue  # game we got was not valid, try again...
                if self.gamePk != _gamePk:
                    self.startNewGame()
                    self.gamePk = _gamePk
                return self.game
            except requests.exceptions.RequestException as e:
                print(
                    f"https://statsapi.mlb.com/api/v1.1/game/{_gamePk}/feed/live "
                    f"request failed (attempt {attempt + 1}/3): {e}"
                )
                if attempt < 2:
                    time.sleep(1)
                else:
                    print(f"Failed to retrieve game (game_pk={_gamePk}) GET request after 3 attempts.")
        return None

    def getGameByFilePath(self, _filePath):
        """Get game from local file given with _filePath. Save and start game if gamePk != -1."""
        with open(_filePath, "r") as f:
            self.game = json.load(f)
        if self.gamePk != self.game.get("gamePk", -1):
            self.startNewGame()
            self.gamePk = self.game.get("gamePk", -1)

    def getRecap(self):
        """Return a game's final outcome (score, winning team, losing team)."""
        if self.situation.awayScore > self.situation.homeScore:
            return (
                f"|  Final score: {self.situation.awayScore}-{self.situation.homeScore}, "
                f"{self.situation.awayTeam} over {self.situation.homeTeam}  |"
            )
        else:
            return (
                f"|  Final score: {self.situation.homeScore}-{self.situation.awayScore}, "
                f"{self.situation.homeTeam} over {self.situation.awayTeam}  |"
            )

    def setPitcher(self, playEvent=None):
        """Set current pitcher. Update pitcher if play event type is a pitching_substitution."""
        if not self.isValid():
            return

        if playEvent is None:
            if self.situation.top:
                self.curPitcher = self.curHomePitcher
            else:
                self.curPitcher = self.curAwayPitcher
            self.situation.setPitcher(self.curPitcher)
            self.situation.setPitchCount(self.pitchCountDict.get(self.situation.pitcher, 0))
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
        """Save lastPitch as situation."""
        self.lastPitch = copy.deepcopy(situation)

    def processAtBatFinished(self, atBatToProcess, output=None):
        """Set score, outs, count, baserunners, and gameOver. Process at bat to post to Threads if threading flagged."""
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
                        self.gameOver = True
                else:
                    if self.situation.homeScore != self.situation.awayScore:
                        self.gameOver = True
            else:
                if not self.situation.top and self.situation.homeScore > self.situation.awayScore:
                    self.gameOver = True
        # Half inning is over but game is not done yet - set outs to 0
        if not self.gameOver and self.situation.outs == 3:
            self.situation.setOuts(0)
            if output:
                if self.situation.top:
                    output.emit(f"Mid {ordinal(self.situation.inning)}.")
                else:
                    output.emit(f"End {ordinal(self.situation.inning)}.")

        # Post last pitch of at bat to threads if it's a big play or scoring play
        if cli.threading:
            # Uncomment to skip posting until at or beyond a specific at bat (debugging purposes)
            # if (atBatToProcess.get("atBatIndex", -1) < 65):
            #     vprint("At bat processed!")
            #     return

            # Uncomment below to post all big plays of a game, even if the game is live
            # And retroactively post big pitches form earlier in the game
            # TODO: make this a flag
            pitch_posting_processor.enqueueAtBatForProcessing(
                self.gamePk, atBatToProcess,
                self.lastPitch,
                self.situation.awayScore,
                self.situation.homeScore
            )
            # Uncomment below to post live game pitches when actually live
            # And don't retroactively post big pitches from earlier in the game
            # TODO: make this a flag
            # curIdx = -1
            # thisBatIdx = -1
            # if self.isLive():
            #     # TODO: make this work to catch up to live and then check win probs from live till end of game.
            #     dprint("game is live")
            #     # numAtBats = len(self.atBats) # 41, 42
            #     # thisBatIdx = 40
            #     # curIdx = index of numAtBats (40, 41)
            #     # during a live game, len of numAtBats is either thisBatIdx +1 or thisBatIdx +2
            #     curIdx = (
            #         self.game.get("liveData", {})
            #         .get("plays", {})
            #         .get("currentPlay", {})
            #         .get("about", {})
            #         .get("atBatIndex", -1)
            #         - 1
            #     )
            #     # -1 because currentPlay atBatIndex is the NEXT at bat to process,
            #     # but this can be wrong because next at bat might not have started yet.
            #     # we want live_game's atBatIndexToProcess val check...
            #     thisBatIdx = atBatToProcess.get("about", {}).get("atBatIndex", -1)
            #     dprint(f"curIdx: {curIdx}")
            #     dprint(f"thisBatIdx: {thisBatIdx}")
            # if not self.isLive() or (self.isLive() and curIdx == thisBatIdx and curIdx != -1):
            #     pitch_posting_processor.enqueueAtBatForProcessing(
            #         self.gamePk,
            #         atBatToProcess,
            #         self.lastPitch,
            #         self.situation.awayScore,
            #         self.situation.homeScore
            #     )
        else:
            vprint(
                "We are not posting a thread right now. "
                "-t or --thread to post a thread. -h or --help for other command line options"
            )

        vprint("At bat processed!")

    def __str__(self):
        """Pretty print return the game and situation for the Game object."""
        return f"{self.game}\ngamePK: {self.gamePk}\nsituation: {self.situation}"


def ordinal(n: int):
    """Human readable number output. Ex: 1st, 2nd, 5th."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
