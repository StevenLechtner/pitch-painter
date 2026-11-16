"""Logic used to print all pitches from a baseball game. Post big plays to Threads if flag enabled."""


# pylint: disable=c-extension-no-member
import sys
import threading
from PySide6 import QtCore
from pitchpainter import cli, pitch_posting_processor, win_probability
from pitchpainter.game import Game, Status
from pitchpainter.print_util import vprint, dprint


class GameProcessorWorker(QtCore.QObject):
    """Thread to print all pitches from game and process each at bat to post to Threads."""

    output = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self, game_pk):
        """Start Threads poster and win probability check threads."""
        super().__init__()
        self.game_pk = game_pk
        self.stop_event = threading.Event()
        pitch_posting_processor.start()

    @QtCore.Slot()
    def run(self):
        """Start printing all pitches from the game by this object's game_pk."""
        processor = GameProcessor(stop_event=self.stop_event, output=self.output, game_pk=self.game_pk)
        processor.print_all_pitches_from_game()
        self.finished.emit()

    def stop(self):
        """Stop this thread from printing pitches and posting big plays to Threads."""
        self.stop_event.set()
        pitch_posting_processor.stop()


class GameProcessor():
    """Handle the events to process an MLB game from start to finish.

    Execute every play event of every at bat of a game with support to post big plays to Threads if specified.
    """

    def __init__(self,
                 stop_event: threading.Event = None,
                 output: QtCore.Signal = None,
                 game_pk: int = -1,
                 filepath: str = None):
        """Initialize the object with a Game by gamePk or filepath, and set stop_event and output attributes.

        The constructor requires one of game_pk or filepath to be provided.
        If both provided, filepath takes precedent.
        The GameProcessor's Game object can be recreated
        """
        if game_pk == -1 and filepath is None:
            raise ValueError("You must provide a 'game_pk' or a 'filepath' to create a valid Game object.")
        self.game = self.create_game(game_pk, filepath)
        self.stop_event = stop_event if stop_event is not None else threading.Event()
        self.output = output
        self.game_pk = game_pk
        self.filepath = filepath

    def create_game(self, game_pk, filepath=None) -> Game:
        """Initialize the Game object.

        Default use this object's game_pk to read game from server.
        Read game from filepath instead if filepath arg provided.
        Return the Game object
        """
        if game_pk == -1 and filepath is None:
            vprint("[GameProcessor] ERROR: You must provide a 'game_pk' or a 'filepath' to create a valid Game object.")
            return None
        game = Game()
        if not filepath:
            game.get_game_by_game_pk(game_pk)
        else:
            game.get_game_by_file_path(filepath)  # read game from filepath instead of the server if provided
        return game

    # TODO: stop using this? Check process_play_event todos
    def is_a_big_play(self, play_event, at_bat_to_process, game: Game):
        """Return True if this at bat resulted in a big play - above THRESHOLD or scoring play. False othersise."""
        if (
            at_bat_to_process.get("about", {}).get("isComplete", False)
            and (at_bat_to_process.get("playEvents", {})[-1].get("index", -1) == play_event.get("index", -1))
        ):
            win_prob = win_probability.WinProbability(game.game_pk)
            return win_prob.is_above_threshold(at_bat_to_process.get("about", {}).get("atBatIndex", -1))
        return False

    def process_play_event(self, play_event, at_bat_to_process):
        """Process a play event.

        A play event is one 'event' inside of a game - could be a pitch, a substitution, a steal, game advisory, etc.
        Any event that affects the game gets processed here - usually processes a pitch, but does more if needed.
        """
        situation = self.game.situation
        play_end_time = play_event.get("endTime", -1).replace(":", "-").replace("T", "_").replace("Z", "")
        situation.set_play_event_id(play_event.get("playId", f"play_end_time_{play_end_time}"))

        if play_event.get("isPitch", False):
            if self.output:
                self.output.emit(situation.draw_pitch())
            self.game.set_last_pitch(situation)
        if self.output:
            self.output.emit(play_event.get("details", {}).get("description", ""))

        # TODO: implement this as another flag - printing every pitch in the game (remove big play stuff...)
        # TODO: figure out what this does, it's been too long
        # playId = playEvent.get("playId", -1)
        # filepath = f"images/{game.game_pk}/{playId}.png"
        # #if (atBatToProcess.get("atBatIndex", -1) >= 65):
        # if cli.threading:
        #     if game.is_live():
        #         print("game is live")
        #         curIdx = (
        #             game.game.get("liveData", {})
        #             .get("plays", {})
        #             .get("currentPlay", {})
        #             .get("about", {})
        #             .get("atBatIndex", -1)
        #         )
        #         thisBatIdx = atBatToProcess.get("about", {}).get("atBatIndex", -1)
        #         print(curIdx)
        #         print(thisBatIdx)
        #         if curIdx == thisBatIdx and curIdx != -1:
        #             if is_a_big_play(playEvent, atBatToProcess, game):
        #                 description = atBatToProcess.get("result", {}).get("description", "")
        #                 postPitchToThreads(situation, filepath, description=description)
        #     else:
        #         if is_a_big_play(playEvent, atBatToProcess, game):
        #             description = atBatToProcess.get("result", {}).get("description", "")
        #             postPitchToThreads(situation, filepath, description=description)
        # else:
        #     vprint(
        #         "We are not posting a thread right now. "
        #         "-t or --thread to post a thread. -h or --help for other command line options"
        #     )

        # update if a run scored mid at bat - wild pitch, stolen home, error on pick off, etc
        scoring_play = play_event.get("details", {}).get("isScoringPlay", False)
        away_score = play_event.get("details", {}).get("awayScore", -1)
        if away_score > -1:
            situation.set_away_score(away_score)
        home_score = play_event.get("details", {}).get("homeScore", -1)
        if home_score > -1:
            situation.set_home_score(home_score)
        if scoring_play:
            description = play_event.get("details", {}).get("description", "")
            pitch_posting_processor.enqueue_pitch_for_processing(
                self.game.game_pk,
                self.game.last_pitch,
                description=description,
                scoring_play=True,
                away_score=situation.away_score,
                home_score=situation.home_score
            )
        # set pitcher for every play event and update pitcher if play event type is a pitching_substitution
        self.game.pitcher_info.set_pitcher(play_event)

        dprint("Is current play complete? ", at_bat_to_process.get("about", {}).get("isComplete", False))
        dprint("Current playEvents[-1] index", at_bat_to_process.get("playEvents", {})[-1].get("index", -1))
        dprint("Current playEvent index", play_event.get("index", -1))
        if (
            at_bat_to_process.get("about", {}).get("isComplete", False)
            and (at_bat_to_process.get("playEvents", {})[-1].get("index", -1) == play_event.get("index", -1))
        ):
            # The at bat is complete - set score, baserunners, and outs, and set balls and strikes to 0
            situation.set_away_score(at_bat_to_process.get("result", {}).get("awayScore", -1))
            situation.set_home_score(at_bat_to_process.get("result", {}).get("homeScore", -1))
            situation.set_outs(at_bat_to_process.get("count", {}).get("outs", -1))
            situation.set_balls(0)
            situation.set_strikes(0)
            situation.set_baserunners_at_end_of_at_bat(at_bat_to_process)
        else:
            # Pitch was thrown - set current count and baserunners
            situation.set_balls(play_event.get("count", {}).get("balls", -1))
            situation.set_strikes(play_event.get("count", {}).get("strikes", -1))
            situation.set_outs(play_event.get("count", {}).get("outs", -1))
            situation.set_baserunners_during_at_bat(at_bat_to_process, play_event.get("index", -1))

        # Incrememnt pitch count for current pitcher
        if play_event.get("isPitch", False):
            pitch_count = self.game.pitcher_info.pitch_count_dict.get(situation.pitcher, 0)
            pitch_count += 1
            self.game.pitcher_info.pitch_count_dict[situation.pitcher] = pitch_count
            situation.set_pitch_count(pitch_count)

    def process_at_bat(self, at_bat_index_to_process):
        """Process this at bat until it is complete."""
        situation = self.game.situation
        at_bat_to_process = self.game.at_bats[at_bat_index_to_process]
        dprint("New at bat. Index: ", at_bat_to_process.get("atBatIndex", -1))
        dprint(f"Now batting: {at_bat_to_process.get("matchup", {}).get("batter", {}).get("fullName", "")}")
        situation.set_inning(at_bat_to_process.get("about", {}).get("inning", -1))
        situation.set_top(at_bat_to_process.get("about", {}).get("isTopInning", False))
        self.game.pitcher_info.set_pitcher()
        situation.set_baserunners_at_start_of_at_bat(at_bat_to_process)

        # Loop through all play events of current play - print when a pitch is thrown
        latest_play_event_index = -1
        current_play_event_to_process = 0
        play_events = at_bat_to_process.get("playEvents", [])
        if self.output:
            self.output.emit(f"{at_bat_to_process["matchup"]["batter"]["fullName"]} now batting.")

        # First process all pitches from currentPlay
        for play_event in play_events:
            self.process_play_event(play_event, at_bat_to_process)
            current_play_event_to_process += 1
        # Then check if the at bat is complete
        if not at_bat_to_process.get("about", {}).get("isComplete", False):
            # If it's not, then wait for it to be complete
            while not (
                at_bat_to_process.get("about", {})
                .get("isComplete", False)
                or current_play_event_to_process <= latest_play_event_index
            ):
                while current_play_event_to_process <= latest_play_event_index:
                    self.process_play_event(play_events[current_play_event_to_process], at_bat_to_process)
                    current_play_event_to_process += 1
                # Ping until a new pitch is thrown
                dprint("Waiting for the next pitch of the at bat...")
                if self.stop_event.wait(2):
                    return
                self.game.get_game_by_game_pk(self.game.game_pk)
                at_bats = self.game.game_feed.get("liveData", {}).get("plays", {}).get("allPlays", [])
                if at_bats:
                    latest_at_bat_index = at_bats[-1].get("atBatIndex", -1)
                else:
                    dprint("atBats len is 0. TODO: Check why...")
                    latest_at_bat_index = -1
                    continue
                dprint("atBatIndexToProcess: ", at_bat_index_to_process)
                dprint("latestAtBatIndex: ", latest_at_bat_index)
                if at_bat_index_to_process <= latest_at_bat_index:
                    at_bat_to_process = at_bats[at_bat_index_to_process]
                    play_events = at_bat_to_process.get("playEvents", [])
                    latest_play_event_index = play_events[-1].get("index", -1) if play_events else -1

        if self.output:
            self.output.emit(at_bat_to_process.get("result", {}).get("description", ""))
        self.game.process_at_bat_finished(at_bat_to_process, self.output)

    def process_all_at_bats_from_game(self):
        """Process all at bats from a baseball game until game is over or stop_event is set."""
        at_bat_index_to_process = 0
        while not self.game.game_over and not self.stop_event.is_set():
            if self.game.at_bats:
                latest_at_bat_index = self.game.at_bats[-1].get("atBatIndex", -1)
            else:
                latest_at_bat_index = -1
            while at_bat_index_to_process > latest_at_bat_index:
                # All at bats have been processed but the game is not over - ping + wait for next at bat from the server
                dprint("Waiting for next at bat to start...")
                if self.stop_event.wait(2):
                    return  # stop_event was sent, return
                self.game.get_game_by_game_pk(self.game.game_pk)
                if self.game.at_bats:
                    latest_at_bat_index = self.game.at_bats[-1].get("atBatIndex", -1)
                else:
                    dprint("atBats len is 0. TODO: Check why...")
                    latest_at_bat_index = -1
                    continue

            # Right here we know that atBatIndexToProcess is <= latestAtBatIndex
            # We process the next at bat at atBatIndexToProcess
            dprint("atBatIndexToProcess", at_bat_index_to_process)
            dprint("latestAtBatIndex", latest_at_bat_index)
            self.process_at_bat(at_bat_index_to_process)
            vprint(
                self.game.at_bats[at_bat_index_to_process]
                .get("result", {})
                .get("description", "")
            )  # print at bat description
            at_bat_index_to_process += 1

    def print_all_pitches_from_game(self, game_pk=-1, filepath=None):
        """Print every siutatuion from a baseball game. The main driver for this entire project."""
        while not self.stop_event.is_set():
            # 1) initialize game if empty, or at least one of game_pk or filepath to read from is passed
            if self.game is None and game_pk == -1 and filepath is None:
                vprint(
                    "Game not set and no 'game_pk' or 'filepath' presented here, "
                    "trying to create a game from the GameProcessor object's 'game_pk' or 'filepath'"
                )
                self.create_game(self.game_pk, self.filepath)
            if game_pk != -1 or filepath:
                self.create_game(game_pk, filepath)
            self.game.set_status()

            # 2) return if game is invalid or game status is preview (game has not started yet)
            if not self.game.is_valid() or self.game.game_status == Status.PREVIEW:
                if self.output:
                    self.output.emit(self.game.game_info)
                return

            # 3) process the entire game
            self.process_all_at_bats_from_game()

            # 4) output the final score
            border = ""
            recap = self.game.get_recap()
            while len(border) < len(recap):
                border += "─"
            border = "+" + border[1:-1] + "+"
            if self.output:
                self.output.emit("")
                self.output.emit(border)
                self.output.emit(recap)
                self.output.emit(border)
            break


# TODO: remove if main removed.
def output_verbose_printing(text):
    """Use output to print to stdout."""
    vprint(text)


# TODO: remove?
def main():
    """Test this file."""
    cli.get_options(sys.argv[1:])
    game_pk = 822765
    test_thread = GameProcessorWorker(game_pk)
    test_thread.output.connect(output_verbose_printing)
    processor = GameProcessor(test_thread.stop_event, test_thread.output)
    processor.print_all_pitches_from_game(game_pk, filepath="tests/pitch_painter/data/live_in_play_runs.json")
    return 0


if __name__ == "__main__":
    main()
