"""
Game Class provides details about a real MLB baseball game. Status Enum specifies game state.

Functionality defines a game:
situation, at bats, pitchers, game state
"""


import copy
import json
import time
from enum import Enum
import requests
import statsapi
from pitchpainter import cli
from pitchpainter import pitch_posting_processor
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
        self.game_pk = -1
        self.situation = Situation()
        self.last_pitch = Situation()
        self.game_info = ""
        self.at_bats = None
        self.cur_away_pitcher = ""
        self.cur_home_pitcher = ""
        self.cur_pitcher = ""
        self.game_status = Status.UNKNOWN
        self.detailed_state = ""
        self.pitch_count_dict = {}
        self.game_over = False

    def is_valid(self):
        """Return True if the game is populated and has at least one at bat. False otherwise."""
        if self.game is None:
            dprint("Game is nothing for some reason")
            self.game_info = "Game is None"
            return False
        self.at_bats = (
            self.game.get("liveData", {})
            .get("plays", {})
            .get("allPlays", [])
        )  # a play is an at bat from this game
        if len(self.at_bats) == 0:
            dprint("Game has not started yet!")
            return False
        return True

    def set_status(self):
        """Set Game status from the game's codedGameState. UNKNOWN if codedGameState can not be found."""
        if self.game is not None:
            status = self.game.get("gameData", {}).get("status", {}).get("codedGameState", "")
            self.detailed_state = self.game.get("gameData", {}).get("status", {}).get("detailedState", "")
            match status:
                case "P" | "S" | "U":
                    self.game_status = Status.PREVIEW
                    self.game_info = f"{self.detailed_state}\nGame has not started yet!"
                case "I" | "M" | "E" | "C" | "D":
                    self.game_status = Status.LIVE
                    self.game_info = f"{self.detailed_state}\nGame in progress!"
                case "F" | "O" | "W" | "A" | "D" | "T" | "R":
                    self.game_status = Status.FINAL
                    self.game_info = f"{self.detailed_state}\nGame has ended!"
                case _:
                    self.game_status = Status.UNKNOWN
                    self.game_info = "Game status unknown!"
        else:
            self.game_status = Status.UNKNOWN
            self.game_info = "Game status unknown; game attribute is None!"
        dprint(f"Game status: {self.game_status} ({status})")

    def is_live(self):
        """Grab Game status, an return True is Game is valid and has a status of LIVE. False otherwise."""
        self.set_status()
        return self.is_valid() and self.game_status == Status.LIVE

    def start_new_game(self):
        """Set up the object for a new game. Populate teams, set pitcher, start the first at bat."""
        if not self.is_valid():
            return
        away_abbr = self.game.get("gameData", {}).get("teams", {}).get("away", {}).get("abbreviation", "[away_team]")
        home_abbr = self.game.get("gameData", {}).get("teams", {}).get("home", {}).get("abbreviation", "[home_team]")
        self.cur_away_pitcher = (
            self.game.get("gameData", {})
            .get("probablePitchers", {})
            .get("away", {})
            .get("fullName", "[away_pitcher]")
        )
        self.at_bats = (
            self.game.get("liveData", {})
            .get("plays", {})
            .get("allPlays", [])
        )  # a play is an at bat from this game
        self.cur_home_pitcher = self.at_bats[0].get("matchup", {}).get("pitcher", {}).get("fullName", "[home_pitcher]")
        self.cur_pitcher = self.cur_home_pitcher
        self.situation = Situation()
        self.situation.start_new_game(home_abbr, away_abbr, self.cur_pitcher)

    # TODO: Test network connection failure
    def get_game_by_game_pk(self, _game_pk):
        """Get game from MLB's server by gamePk.

        Attempt to gather data up to three times.
        Save, start, and return game if valid.
        Return None if game can not be found.
        """
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            try:
                self.game = statsapi.get('game', {'gamePk': _game_pk})
                if not self.is_valid():
                    continue  # game we got was not valid, try again...
                if self.game_pk != _game_pk:
                    self.start_new_game()
                    self.game_pk = _game_pk
                return self.game
            except requests.exceptions.RequestException as e:
                print(
                    f"https://statsapi.mlb.com/api/v1.1/game/{_game_pk}/feed/live "
                    f"request failed (attempt {attempt + 1}/3): {e}"
                )
                if attempt < 2:
                    time.sleep(1)
                else:
                    print(f"Failed to retrieve game (game_pk={_game_pk}) GET request after 3 attempts.")
        return None

    def get_game_by_file_path(self, _filepath):
        """Get game from local file given with _filepath. Save and start game if game_pk != -1."""
        with open(_filepath, "r", encoding="utf-8") as f:
            self.game = json.load(f)
        if self.game_pk != self.game.get("gamePk", -1):
            self.start_new_game()
            self.game_pk = self.game.get("gamePk", -1)

    def get_recap(self):
        """Return a game's final outcome (score, winning team, losing team)."""
        if self.situation.away_score > self.situation.home_score:
            return (
                f"|  Final score: {self.situation.away_score}-{self.situation.home_score}, "
                f"{self.situation.away_team} over {self.situation.home_team}  |"
            )
        return (
            f"|  Final score: {self.situation.home_score}-{self.situation.away_score}, "
            f"{self.situation.home_team} over {self.situation.away_team}  |"
        )

    def set_pitcher(self, play_event=None):
        """Set current pitcher. Update pitcher if play event type is a pitching_substitution."""
        if not self.is_valid():
            return

        if play_event is None:
            if self.situation.top:
                self.cur_pitcher = self.cur_home_pitcher
            else:
                self.cur_pitcher = self.cur_away_pitcher
            self.situation.set_pitcher(self.cur_pitcher)
            self.situation.set_pitch_count(self.pitch_count_dict.get(self.situation.pitcher, 0))
            return

        default = "[home_pitcher]" if self.situation.top else "[away_pitcher]"
        pitcher = default
        if play_event.get("details", {}).get("eventType", "") == "pitching_substitution":
            player_id = play_event.get("player", {}).get("id", -1)
            pitcher = (
                self.game.get("gameData", {})
                .get("players", {})
                .get(f"ID{player_id}", {})
                .get("fullName", default)
            )
            if self.situation.top:
                self.cur_home_pitcher = pitcher
            else:
                self.cur_away_pitcher = pitcher
        self.set_pitcher()

    def set_last_pitch(self, situation: Situation):
        """Save last_pitch as situation."""
        self.last_pitch = copy.deepcopy(situation)

    def process_at_bat_finished(self, at_bat_to_process, output=None):
        """Set score, outs, count, baserunners, and game_over. Process at bat, post to Threads if threading flagged."""
        vprint("Processing at bat finished...")
        self.situation.set_away_score(at_bat_to_process.get("result", {}).get("awayScore", -1))
        self.situation.set_home_score(at_bat_to_process.get("result", {}).get("homeScore", -1))
        self.situation.set_outs(at_bat_to_process.get("count", {}).get("outs", -1))
        self.situation.set_balls(0)
        self.situation.set_strikes(0)
        self.situation.set_baserunners_at_end_of_at_bat(at_bat_to_process)
        # Check if the result of this at bat finished the game
        if self.situation.inning >= 9:
            if self.situation.outs >= 3:
                if self.situation.top:
                    if self.situation.home_score > self.situation.away_score:
                        self.game_over = True
                else:
                    if self.situation.home_score != self.situation.away_score:
                        self.game_over = True
            else:
                if not self.situation.top and self.situation.home_score > self.situation.away_score:
                    self.game_over = True
        # Half inning is over but game is not done yet - set outs to 0
        if not self.game_over and self.situation.outs == 3:
            self.situation.set_outs(0)
            if output:
                if self.situation.top:
                    output.emit(f"Mid {ordinal(self.situation.inning)}.")
                else:
                    output.emit(f"End {ordinal(self.situation.inning)}.")

        # Post last pitch of at bat to threads if it's a big play or scoring play
        if cli.threading:
            # Uncomment to skip posting until at or beyond a specific at bat (debugging purposes)
            # if (at_bat_to_process.get("atBatIndex", -1) < 65):
            #     vprint("At bat processed!")
            #     return

            # Uncomment below to post all big plays of a game, even if the game is live
            # And retroactively post big pitches form earlier in the game
            # TODO: make this a flag
            pitch_posting_processor.enqueue_at_bat_for_processing(
                self.game_pk,
                at_bat_to_process,
                self.last_pitch,
                self.situation.away_score,
                self.situation.home_score
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
            #     thisBatIdx = at_bat_to_process.get("about", {}).get("atBatIndex", -1)
            #     dprint(f"curIdx: {curIdx}")
            #     dprint(f"thisBatIdx: {thisBatIdx}")
            # if not self.isLive() or (self.isLive() and curIdx == thisBatIdx and curIdx != -1):
            #     pitch_posting_processor.enqueueAtBatForProcessing(
            #         self.game_pk,
            #         at_bat_to_process,
            #         self.last_pitch,
            #         self.situation.away_score,
            #         self.situation.home_score
            #     )
        else:
            vprint(
                "We are not posting a thread right now. "
                "-t or --thread to post a thread. -h or --help for other command line options"
            )

        vprint("At bat processed!")

    def __str__(self):
        """Pretty print return the game and situation for the Game object."""
        return f"{self.game}\ngamePK: {self.game_pk}\nsituation: {self.situation}"


def ordinal(n: int):
    """Human readable number output. Ex: 1st, 2nd, 5th."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
