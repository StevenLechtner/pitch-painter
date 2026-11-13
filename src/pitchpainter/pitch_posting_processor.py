"""Helper module to check, configure, and post a pitch to Threads."""


import copy
import datetime
import threading
import pitchpainter.pitchbypitch as pitchbypitch
import pitchpainter.thread_poster as thread_poster
import pitchpainter.win_probability as win_probability
from pitchpainter.print_util import dprint
from PySide6.QtCore import QRunnable, QThreadPool

pitchPool = QThreadPool()
pitchPool.setMaxThreadCount(1)
stop_event = threading.Event()


def stop():
    """Stop Thread posting and win probability threads."""
    dprint("pitch_posting_processor stop_event is True")
    stop_event.set()
    pitchPool.clear()
    win_probability.stop()
    thread_poster.stop()


def start():
    """Start Thread posting and win probability threads."""
    dprint("pitch_posting_processor stop_event is False")
    stop_event.clear()
    win_probability.start()
    thread_poster.start()


def postToThreads(gamePk, playEventId, pitchToPost, awayScore, homeScore, scoringPlay, description):
    """Get desired text from a situation and post to Threads."""
    now = datetime.datetime.now()
    curTime = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.{now.microsecond // 1000:03d}"
    filepath = f"images/{gamePk}/play_id_{playEventId}_created_{curTime}.png"
    if scoringPlay and awayScore > -1 and homeScore > -1:
        text = pitchbypitch.drawPitchWithScoreUpdate(awayScore, homeScore, pitchToPost)
        altText = pitchbypitch.drawPitchWithScoreAltText(awayScore, homeScore, pitchToPost)
    else:
        text = pitchbypitch.drawPitch(pitchToPost)
        altText = pitchbypitch.drawPitchForTweeting(pitchToPost)
    thread_poster.postThreadTextAsImage(text, descriptionText=description, altText=altText, filepath=filepath)


def processAndPostPitch(gamePk, atBatToProcess, playEventId, pitchToPost, awayScore, homeScore):
    """Process the pitch and post to Threads if it is a big play."""
    winProb = win_probability.WinProbability(gamePk)
    if winProb.isABigPlay(atBatToProcess.get("about", {}).get("atBatIndex", -1)):
        description = atBatToProcess.get("result", {}).get("description", "")
        scoringPlay = atBatToProcess.get("about", {}).get("isScoringPlay", False)
        postToThreads(gamePk, playEventId, pitchToPost, awayScore, homeScore, scoringPlay, description)


class AtBatQueue(QRunnable):
    """Queue at bats to process and post to Threads as a background thread."""

    def __init__(self, gamePk, atBatToProcess, lastPitch, awayScore, homeScore):
        """Set object variables given arguments."""
        super().__init__()
        self.pitchToPost = copy.deepcopy(lastPitch)
        self.gamePk = gamePk
        self.atBatToProcess = atBatToProcess
        self.playEventId = lastPitch.playEventId
        self.awayScore = awayScore
        self.homeScore = homeScore

    def run(self):
        """Process at bat and post to Threads if it fits the requirements."""
        processAndPostPitch(
            self.gamePk,
            self.atBatToProcess,
            self.playEventId,
            self.pitchToPost,
            self.awayScore,
            self.homeScore
        )


class PitchQueue(QRunnable):
    """Queue pitches to process and post to Threads as a background thread."""

    def __init__(self, gamePk, lastPitch, description, scoringPlay, awayScore, homeScore):
        """Set object variables given arguments."""
        super().__init__()
        self.pitchToPost = copy.deepcopy(lastPitch)
        self.gamePk = gamePk
        self.playEventId = lastPitch.playEventId
        self.description = description
        self.awayScore = awayScore
        self.homeScore = homeScore
        self.scoringPlay = scoringPlay

    def run(self):
        """Process pitch and post to Threads if it fits the requirements."""
        postToThreads(
            self.gamePk,
            self.playEventId,
            self.pitchToPost,
            self.awayScore,
            self.homeScore,
            self.scoringPlay,
            self.description
        )


def enqueueAtBatForProcessing(gamePk, atBatToProcess, lastPitch, awayScore, homeScore):
    """Create the at bat queue and add the at bat to the pitch pool to process pitch in the background thread."""
    abQueue = AtBatQueue(gamePk, atBatToProcess, lastPitch, awayScore, homeScore)
    pitchPool.start(abQueue)


def enqueuePitchForProcessing(gamePk, lastPitch, description, scoringPlay, awayScore, homeScore):
    """Create the pitch queue and add the pitch to the pitch pool to process pitch in the background thread."""
    pQueue = PitchQueue(gamePk, lastPitch, description, scoringPlay, awayScore, homeScore)
    pitchPool.start(pQueue)
