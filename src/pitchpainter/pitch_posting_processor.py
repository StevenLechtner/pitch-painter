"""Helper module to check, configure, and post a pitch to Threads."""


# pylint: disable=c-extension-no-member, no-name-in-module, too-few-public-methods
import copy
import datetime
import threading
from dataclasses import dataclass
from PySide6.QtCore import QRunnable, QThreadPool
from pitchpainter import thread_poster, win_probability
from pitchpainter.print_util import dprint
from pitchpainter.situation import Situation

pitch_pool = QThreadPool()
pitch_pool.setMaxThreadCount(1)
stop_event = threading.Event()


@dataclass
class AtBatContainer:
    """Context container for processing and posting an at bat to Threads if it's a big play."""

    game_pk: int
    at_bat_to_process: dict
    pitch_to_post: Situation
    away_score: int
    home_score: int


@dataclass
class PitchContainer:
    """Context container for posting a pitch to Threads."""

    game_pk: int
    pitch_to_post: Situation
    description: str
    scoring_play: bool
    away_score: int
    home_score: int


def stop():
    """Stop Thread posting and win probability threads."""
    dprint("pitch_posting_processor stop_event is True")
    stop_event.set()
    pitch_pool.clear()
    win_probability.stop()
    thread_poster.stop()


def start():
    """Start Thread posting and win probability threads."""
    dprint("pitch_posting_processor stop_event is False")
    stop_event.clear()
    win_probability.start()
    thread_poster.start()


def post_to_threads(context: PitchContainer):
    """Get desired text from a situation and post to Threads."""
    now = datetime.datetime.now()
    cur_time = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
    filepath = f"images/{context.game_pk}/play_id_{context.pitch_to_post.play_event_id}_created_{cur_time}.png"
    if context.scoring_play and context.away_score > -1 and context.home_score > -1:
        text = context.pitch_to_post.draw_pitch_with_score(context.away_score, context.home_score)
        alt_text = context.pitch_to_post.draw_pitch_with_score(context.away_score, context.home_score, alt_text=True)
    else:
        text = context.pitch_to_post.draw_pitch()
        alt_text = context.pitch_to_post.draw_pitch(alt_text=True)
    thread_poster.post_thread_text_as_image(
        text,
        description_text=context.description,
        alt_text=alt_text,
        filepath=filepath
    )


def process_and_post_pitch(context: AtBatContainer):
    """Process the pitch and post to Threads if it is a big play."""
    win_prob = win_probability.WinProbability(context.game_pk)
    if win_prob.is_a_big_play(context.at_bat_to_process.get("about", {}).get("atBatIndex", -1)):
        description = context.at_bat_to_process.get("result", {}).get("description", "")
        scoring_play = context.at_bat_to_process.get("about", {}).get("isScoringPlay", False)
        pitch_context = PitchContainer(
            game_pk=context.game_pk,
            pitch_to_post=copy.deepcopy(context.pitch_to_post),
            description=description,
            scoring_play=scoring_play,
            away_score=context.away_score,
            home_score=context.home_score
        )
        post_to_threads(pitch_context)


class AtBatQueue(QRunnable):
    """Queue at bats to process and post to Threads as a background thread."""

    def __init__(self, game_pk, at_bat_to_process, last_pitch, away_score, home_score):
        """Set object variables given arguments."""
        super().__init__()
        self.context = AtBatContainer(
            game_pk=game_pk,
            at_bat_to_process=at_bat_to_process,
            pitch_to_post=copy.deepcopy(last_pitch),
            away_score=away_score,
            home_score=home_score
        )

    def run(self):
        """Process at bat and post to Threads if it fits the requirements."""
        process_and_post_pitch(self.context)


class PitchQueue(QRunnable):
    """Queue pitches to process and post to Threads as a background thread."""

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    # an extra argument or two to create the PitchContainer is fine here
    def __init__(self, game_pk, last_pitch, description, scoring_play, away_score, home_score):
        """Set object variables given arguments."""
        super().__init__()
        self.context = PitchContainer(
            game_pk=game_pk,
            pitch_to_post=copy.deepcopy(last_pitch),
            description=description,
            scoring_play=scoring_play,
            away_score=away_score,
            home_score=home_score
        )

    def run(self):
        """Process pitch and post to Threads if it fits the requirements."""
        post_to_threads(self.context)


def enqueue_at_bat_for_processing(game_pk, at_bat_to_process, last_pitch, away_score, home_score):
    """Create the at bat queue and add the at bat to the pitch pool to process pitch in the background thread."""
    ab_queue = AtBatQueue(game_pk, at_bat_to_process, last_pitch, away_score, home_score)
    pitch_pool.start(ab_queue)


# pylint: disable=too-many-arguments, too-many-positional-arguments
# an extra argument or two to create the PitchQueue is fine here
def enqueue_pitch_for_processing(game_pk, last_pitch, description, scoring_play, away_score, home_score):
    """Create the pitch queue and add the pitch to the pitch pool to process pitch in the background thread."""
    p_queue = PitchQueue(game_pk, last_pitch, description, scoring_play, away_score, home_score)
    pitch_pool.start(p_queue)
