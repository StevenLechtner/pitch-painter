import copy
import datetime
import threading
import pitchbypitch
import thread_poster
import win_probability
from PySide6.QtCore import QRunnable, QThreadPool

pitchPool = QThreadPool()
pitchPool.setMaxThreadCount(1)
stop_event = threading.Event()

def stop():
    print("pitch_posting_processor stop_event is True")
    stop_event.set()
    pitchPool.clear()
    win_probability.stop()
    thread_poster.stop()

def start():
    print("pitch_posting_processor stop_event is False")
    stop_event.clear()
    win_probability.start()
    thread_poster.start()

def postToThreads(gamePk, playEventId, pitchToPost, awayScore, homeScore, scoringPlay, description):
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
    winProb = win_probability.WinProbability(gamePk)
    if winProb.isABigPlay(atBatToProcess.get("about", {}).get("atBatIndex", -1)):
        description = atBatToProcess.get("result", {}).get("description", "")
        scoringPlay = atBatToProcess.get("about", {}).get("isScoringPlay", False)
        postToThreads(gamePk, playEventId, pitchToPost, awayScore, homeScore, scoringPlay, description)

class AtBatQueue(QRunnable):

    def __init__(self, gamePk, atBatToProcess, lastPitch, awayScore, homeScore):
        super().__init__()
        self.pitchToPost = copy.deepcopy(lastPitch)
        self.gamePk = gamePk
        self.atBatToProcess = atBatToProcess
        self.playEventId = lastPitch.playEventId
        self.awayScore = awayScore
        self.homeScore = homeScore

    def run(self):
        processAndPostPitch(self.gamePk, self.atBatToProcess, self.playEventId, self.pitchToPost, self.awayScore, self.homeScore)

class PitchQueue(QRunnable):

    def __init__(self, gamePk, lastPitch, description, scoringPlay, awayScore, homeScore):
        super().__init__()
        self.pitchToPost = copy.deepcopy(lastPitch)
        self.gamePk = gamePk
        self.playEventId = lastPitch.playEventId
        self.description = description
        self.awayScore = awayScore
        self.homeScore = homeScore
        self.scoringPlay = scoringPlay

    def run(self):
        postToThreads(self.gamePk, self.playEventId, self.pitchToPost, self.awayScore, self.homeScore, self.scoringPlay, self.description)

def enqueueAtBatForProcessing(gamePk, atBatToProcess, lastPitch, awayScore, homeScore):
    abQueue = AtBatQueue(gamePk, atBatToProcess, lastPitch, awayScore, homeScore)
    pitchPool.start(abQueue)

def enqueuePitchForProcessing(gamePk, lastPitch, description, scoringPlay, awayScore, homeScore):
    pQueue = PitchQueue(gamePk, lastPitch, description, scoringPlay, awayScore, homeScore)
    pitchPool.start(pQueue)
