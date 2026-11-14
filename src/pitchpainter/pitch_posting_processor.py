"""Helper module to check, configure, and post a pitch to Threads."""


# pylint: disable=c-extension-no-member, no-name-in-module
import copy
import datetime
import threading
from PySide6.QtCore import QRunnable, QThreadPool
from pitchpainter import pitchbypitch, thread_poster, win_probability
from pitchpainter.print_util import dprint

pitch_pool = QThreadPool()
pitch_pool.setMaxThreadCount(1)
stop_event = threading.Event()


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


def post_to_threads(game_pk, play_event_id, pitch_to_post, away_score, home_score, scoring_play, description):
    """Get desired text from a situation and post to Threads."""
    now = datetime.datetime.now()
    cur_time = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
    filepath = f"images/{game_pk}/play_id_{play_event_id}_created_{cur_time}.png"
    if scoring_play and away_score > -1 and home_score > -1:
        text = pitchbypitch.draw_pitch_with_score_update(away_score, home_score, pitch_to_post)
        alt_text = pitchbypitch.draw_pitch_with_score_alt_text(away_score, home_score, pitch_to_post)
    else:
        text = pitchbypitch.draw_pitch(pitch_to_post)
        alt_text = pitchbypitch.draw_pitch_for_tweeting(pitch_to_post)
    thread_poster.post_thread_text_as_image(text, description_text=description, alt_text=alt_text, filepath=filepath)


def process_and_post_pitch(game_pk, at_bat_to_process, play_event_id, pitch_to_post, away_score, home_score):
    """Process the pitch and post to Threads if it is a big play."""
    win_prob = win_probability.WinProbability(game_pk)
    if win_prob.is_a_big_play(at_bat_to_process.get("about", {}).get("atBatIndex", -1)):
        description = at_bat_to_process.get("result", {}).get("description", "")
        scoring_play = at_bat_to_process.get("about", {}).get("isScoringPlay", False)
        post_to_threads(game_pk, play_event_id, pitch_to_post, away_score, home_score, scoring_play, description)


class AtBatQueue(QRunnable):
    """Queue at bats to process and post to Threads as a background thread."""

    def __init__(self, game_pk, at_bat_to_process, last_pitch, away_score, home_score):
        """Set object variables given arguments."""
        super().__init__()
        self.pitch_to_post = copy.deepcopy(last_pitch)
        self.game_pk = game_pk
        self.at_bat_to_process = at_bat_to_process
        self.play_event_id = last_pitch.play_event_id
        self.away_score = away_score
        self.home_score = home_score

    def run(self):
        """Process at bat and post to Threads if it fits the requirements."""
        process_and_post_pitch(
            self.game_pk,
            self.at_bat_to_process,
            self.play_event_id,
            self.pitch_to_post,
            self.away_score,
            self.home_score
        )


class PitchQueue(QRunnable):
    """Queue pitches to process and post to Threads as a background thread."""

    def __init__(self, game_pk, last_pitch, description, scoring_play, away_score, home_score):
        """Set object variables given arguments."""
        super().__init__()
        self.pitch_to_post = copy.deepcopy(last_pitch)
        self.game_pk = game_pk
        self.play_event_id = last_pitch.play_event_id
        self.description = description
        self.away_score = away_score
        self.home_score = home_score
        self.scoring_play = scoring_play

    def run(self):
        """Process pitch and post to Threads if it fits the requirements."""
        post_to_threads(
            self.game_pk,
            self.play_event_id,
            self.pitch_to_post,
            self.away_score,
            self.home_score,
            self.scoring_play,
            self.description
        )


def enqueue_at_bat_for_processing(game_pk, at_bat_to_process, last_pitch, away_score, home_score):
    """Create the at bat queue and add the at bat to the pitch pool to process pitch in the background thread."""
    ab_queue = AtBatQueue(game_pk, at_bat_to_process, last_pitch, away_score, home_score)
    pitch_pool.start(ab_queue)


def enqueue_pitch_for_processing(game_pk, last_pitch, description, scoring_play, away_score, home_score):
    """Create the pitch queue and add the pitch to the pitch pool to process pitch in the background thread."""
    p_queue = PitchQueue(game_pk, last_pitch, description, scoring_play, away_score, home_score)
    pitch_pool.start(p_queue)
