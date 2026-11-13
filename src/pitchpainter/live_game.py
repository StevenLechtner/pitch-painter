"""Logic used to print all pitches from a baseball game. Post big plays to Threads if flag enabled."""


# pylint: disable=c-extension-no-member
import json
import sys
import threading
import statsapi
from PySide6 import QtCore
from pitchpainter import cli
from pitchpainter import pitch_posting_processor
from pitchpainter import win_probability
from pitchpainter.game import Game, Status
from pitchpainter.pitchbypitch import drawPitch, postPitchToThreads
from pitchpainter.print_util import vprint, dprint


class LiveGameWorker(QtCore.QObject):
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
        print_all_pitches_from_game(self.game_pk, self.output, self.stop_event)
        self.finished.emit()

    def stop(self):
        """Stop this thread from printing pitches and posting big plays to Threads."""
        self.stop_event.set()
        pitch_posting_processor.stop()


# TODO: stop using this?
def is_a_big_play(play_event, at_bat_to_process, game):
    """Return True if this at bat resulted in a big play - above THRESHOLD or scoring play. False othersise."""
    if (
        at_bat_to_process.get("about", {}).get("isComplete", False)
        and (at_bat_to_process.get("playEvents", {})[-1].get("index", -1) == play_event.get("index", -1))
    ):
        win_prob = win_probability.WinProbability(game.game_pk)
        return win_prob.isAboveThreshold(at_bat_to_process.get("about", {}).get("atBatIndex", -1))
    return False


def process_play_event(play_event, situation, at_bat_to_process, game, output):
    """Process a play event.

    A play event is one 'event' inside of a game - could be a pitch, a substitution, a steal, game advisory, etc.
    Any event that affects the game gets processed here - usually processes a pitch, but does more if needed.
    """
    play_end_time = play_event.get("endTime", -1).replace(":", "-").replace("T", "_").replace("Z", "")
    situation.setPlayEventId(play_event.get("playId", f"play_end_time_{play_end_time}"))

    if play_event.get("isPitch", False):
        if output:
            output.emit(drawPitch(situation))
        game.set_last_pitch(situation)
    if output:
        output.emit(play_event.get("details", {}).get("description", ""))

    # TODO: implement this as another flag - printing every pitch in the game (remove big play stuff...)
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
        situation.setAwayScore(away_score)
    home_score = play_event.get("details", {}).get("homeScore", -1)
    if home_score > -1:
        situation.setHomeScore(home_score)
    if scoring_play:
        description = play_event.get("details", {}).get("description", "")
        pitch_posting_processor.enqueuePitchForProcessing(
            game.game_pk,
            game.last_pitch,
            description=description,
            scoringPlay=True,
            awayScore=situation.awayScore,
            homeScore=situation.homeScore
        )
    # set pitcher for every play event and update pitcher if play event type is a pitching_substitution
    game.set_pitcher(play_event)

    dprint("Is current play complete? ", at_bat_to_process.get("about", {}).get("isComplete", False))
    dprint("Current playEvents[-1] index", at_bat_to_process.get("playEvents", {})[-1].get("index", -1))
    dprint("Current playEvent index", play_event.get("index", -1))
    if (
        at_bat_to_process.get("about", {}).get("isComplete", False)
        and (at_bat_to_process.get("playEvents", {})[-1].get("index", -1) == play_event.get("index", -1))
    ):
        # The at bat is complete - set score, baserunners, and outs, and set balls and strikes to 0
        situation.setAwayScore(at_bat_to_process.get("result", {}).get("awayScore", -1))
        situation.setHomeScore(at_bat_to_process.get("result", {}).get("homeScore", -1))
        situation.setOuts(at_bat_to_process.get("count", {}).get("outs", -1))
        situation.setBalls(0)
        situation.setStrikes(0)
        situation.setBaserunnersAtEndOfAtBat(at_bat_to_process)
    else:
        # Pitch was thrown - set current count and baserunners
        situation.setBalls(play_event.get("count", {}).get("balls", -1))
        situation.setStrikes(play_event.get("count", {}).get("strikes", -1))
        situation.setOuts(play_event.get("count", {}).get("outs", -1))
        situation.setBaserunnersDuringAtBat(at_bat_to_process, play_event.get("index", -1))

    # Incrememnt pitch count for current pitcher
    if play_event.get("isPitch", False):
        pitch_count = game.pitch_count_dict.get(situation.pitcher, 0)
        pitch_count += 1
        game.pitch_count_dict[situation.pitcher] = pitch_count
        situation.setPitchCount(pitch_count)


def process_at_bat(game, at_bat_index_to_process, output, game_pk, stop_event):
    """Process this at bat until it is complete."""
    situation = game.situation
    at_bat_to_process = game.at_bats[at_bat_index_to_process]
    dprint("New at bat. Index: ", at_bat_to_process.get("atBatIndex", -1))
    dprint(f"Now batting: {at_bat_to_process.get("matchup", {}).get("batter", {}).get("fullName", "")}")
    situation.setInning(at_bat_to_process.get("about", {}).get("inning", -1))
    situation.setTop(at_bat_to_process.get("about", {}).get("isTopInning", False))
    game.set_pitcher()  # set pitcher when new at bat starts to account for inning change
    situation.setBaserunnersAtStartOfAtBat(at_bat_to_process)

    # Loop through all play events of current play - print when a pitch is thrown
    latest_play_event_index = -1
    current_play_event_to_process = 0
    play_events = at_bat_to_process.get("playEvents", [])
    if output:
        output.emit(f"{at_bat_to_process["matchup"]["batter"]["fullName"]} now batting.")

    # First process all pitches from currentPlay
    for play_event in play_events:
        process_play_event(play_event, situation, at_bat_to_process, game, output)
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
                process_play_event(
                    play_events[current_play_event_to_process],
                    situation,
                    at_bat_to_process,
                    game,
                    output
                )
                current_play_event_to_process += 1
            # Ping until a new pitch is thrown
            dprint("Waiting for the next pitch of the at bat...")
            if stop_event.wait(2):
                return
            game.get_game_by_game_pk(game_pk)
            at_bats = game.game.get("liveData", {}).get("plays", {}).get("allPlays", [])
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

    if output:
        output.emit(at_bat_to_process.get("result", {}).get("description", ""))
    game.process_at_bat_finished(at_bat_to_process, output)


def print_all_pitches_from_game(game_pk, output, stop_event, filepath=None):
    """Print every siutatuion from a baseball game. The main driver for this entire project."""
    while not stop_event.is_set():
        game = Game()
        if not filepath:
            game.get_game_by_game_pk(game_pk)
        else:
            game.get_game_by_file_path(filepath)  # test from a json file instead of the server if filepath provided
        game.set_status()
        if not game.is_valid() or game.game_status == Status.PREVIEW:
            if output:
                output.emit(game.game_info)
            return

        at_bat_index_to_process = 0
        while not game.game_over and not stop_event.is_set():
            if game.at_bats:
                latest_at_bat_index = game.at_bats[-1].get("atBatIndex", -1)
            else:
                latest_at_bat_index = -1
            while at_bat_index_to_process > latest_at_bat_index:
                # All at bats have been processed but the game is not over - ping + wait for next at bat from the server
                dprint("Waiting for next at bat to start...")
                if stop_event.wait(2):
                    return  # stop_event was sent, return
                game.get_game_by_game_pk(game.game_pk)
                if game.at_bats:
                    latest_at_bat_index = game.at_bats[-1].get("atBatIndex", -1)
                else:
                    dprint("atBats len is 0. TODO: Check why...")
                    latest_at_bat_index = -1
                    continue

            # Right here we know that atBatIndexToProcess is <= latestAtBatIndex
            # We process the next at bat at atBatIndexToProcess
            dprint("atBatIndexToProcess", at_bat_index_to_process)
            dprint("latestAtBatIndex", latest_at_bat_index)
            process_at_bat(game, at_bat_index_to_process, output, game.game_pk, stop_event)
            vprint(
                game.at_bats[at_bat_index_to_process]
                .get("result", {})
                .get("description", "")
            )  # print at bat description
            at_bat_index_to_process += 1

        # additional check - stop_event got set within processAtBat()
        if stop_event.is_set():
            return

        border = ""
        recap = game.get_recap()
        while len(border) < len(recap):
            border += "─"
        border = "+" + border[1:-1] + "+"
        if output:
            output.emit("")
            output.emit(border)
            output.emit(recap)
            output.emit(border)
        return


# TODO: remove.
def output_verbose_printing(text):
    """Use output to print to stdout."""
    vprint(text)


# TODO: remove?
def main():
    """Test this file."""
    # +======================+
    # |   Live Play Output   |
    # +======================+
    cli.get_options(sys.argv[1:])

    # game = statsapi.get('game', {'gamePk': 776189})
    # # with open("tests/meadows.json", "r") as f:
    # # # with open("tests/example_out.json", "r") as f:
    # #     game = json.load(f)
    # pitchbypitch.printLiveGame(game)
    # printTeamName(116)

    # game = statsapi.get('game', {'gamePk': game_pk})
    # game_pk = 823989
    # game_pk = 745369
    game_pk = 822765
    test_thread = LiveGameWorker(game_pk)
    test_thread.output.connect(output_verbose_printing)
    print_all_pitches_from_game(game_pk,
                                test_thread.output,
                                test_thread.stop_event,
                                filepath="tests/pitch_painter/data/live_in_play_runs.json")
    return 0


if __name__ == "__main__":
    main()
