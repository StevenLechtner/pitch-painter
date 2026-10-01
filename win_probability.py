import cli
import heapq
import requests
import statsapi
import sys
import threading
from print_util import dprint

stop_event = threading.Event()

def stop():
    print("win_probability stop_event is True")
    stop_event.set()

def start():
    print("win_probability stop_event is False")
    stop_event.clear()

class WinProbability():
    # score weights
    NORM_PROBS_ADDED = 25
    NORM_LEV_IDX = 2.5
    NORM_DRAMA_IDX = 150
    PROBS_ADDED_WEIGHT = 0.7
    LEV_IDX_WEIGHT = 0.15
    DRAMA_IDX_WEIGHT = 0.15
    THRESHOLD = 0.375
    def __init__(self, gamePk=None):
        self.gamePk = -1 if gamePk is None else gamePk
        self.winProbabilities: list[WinProbabilityInfo] = self.setWinProbabilities() # List of WinProbabilityInfo
        # Top ten: List of tuples (x, y) where x is the metric and y is the at bat index
        self.topTenProbsAdded = []
        self.topTenLevIdx = []
        self.topTenDramaIdx = []
        self.scores = []
        self.topTenScores = []

    def getGameWinProbabilities(self):
        if stop_event.is_set():
            return []

        winProbabilityList = []
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            if stop_event.is_set():
                return []
            try:
                winProbabilityList = statsapi.get('game_winProbability', {'gamePk': self.gamePk})
                if winProbabilityList:
                    return winProbabilityList
            except requests.exceptions.RequestException as e:
                print(f"https://statsapi.mlb.com/api/v1.1/game/{self.gamePk}/winProbability request failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    if stop_event.wait(1):
                        return []
                else:
                    print(f"Failed to retrieve win probability (game_pk={self.gamePk}) GET request after 3 attempts.")
                    winProbabilityList.clear()
        return []

    def getFinishedAtBat(self, atBatIndex):
        # wait for at bat at given atBatIndex to be complete with win probability numbers
        # just check if the next atBatIndex is present
        # if not, check if a win probability is 100% (indicates game over)
        winProbabilityList = []
        # TODO: don't make this an "infinite" loop. Check for a max of 5(ish) minutes? Determine how long it takes to be 100% sure that the values are updated
        # TODO: Additional check - see if any values are different (win prob, drama, lev) - different indicates they're updated, but they could be updated to the same...
        while not stop_event.is_set():
            winProbabilityList = self.getGameWinProbabilities()
            if not winProbabilityList:
                # win probabilities list is empty!
                if stop_event.wait(5):
                    return None
                else:
                    continue
            latestAtBat = winProbabilityList[-1]
            latestAtBatIndex = latestAtBat.get("atBatIndex", -1)
            if latestAtBatIndex > atBatIndex:
                # there is a new at bat, this at bat is complete
                break
            elif latestAtBatIndex < atBatIndex:
                # error check: this at bat has not even happened yet
                dprint(f"Win probability at bat has not happened yet! {atBatIndex} < {latestAtBatIndex}")
                break
            elif latestAtBat.get("homeTeamWinProbability", -1) >= 100 or latestAtBat.get("awayTeamWinProbability", -1) >= 100:
                # no new at bat because the game is over, this at bat is complete
                break
            else:
                # at bat is not yet complete
                if stop_event.wait(5):
                    return

        for atBat in winProbabilityList:
            if atBat.get("atBatIndex", -1) == atBatIndex:
                return atBat
        return None

    def getWinProbabilityInfo(self, atBat):
        homeProb = atBat.get("homeTeamWinProbability", 0.0)
        awayProb = atBat.get("awayTeamWinProbability", 0.0)
        homeProbAdded = atBat.get("homeTeamWinProbabilityAdded", 0.0)
        levIdx = atBat.get("leverageIndex", 0.0)
        dramaIdx = atBat.get("dramaIndex", 0.0)
        atBatIdx = atBat.get("atBatIndex", 0.0)
        return WinProbabilityInfo(homeProb, awayProb, homeProbAdded, levIdx, dramaIdx, atBatIdx)

    def isAboveThreshold(self, atBatIndex):
        atBat = self.getFinishedAtBat(atBatIndex)
        if atBat is None:
            return False

        winProb = self.getWinProbabilityInfo(atBat)
        probsAddedVal = abs(winProb.homeTeamWinProbabilityAdded)
        levIdxVal = winProb.leverageIndex
        dramaIdxVal = winProb.dramaIndex
        score = (
            self.PROBS_ADDED_WEIGHT * (probsAddedVal / self.NORM_PROBS_ADDED) 
            + self.LEV_IDX_WEIGHT * (levIdxVal / self.NORM_LEV_IDX) 
            + self.DRAMA_IDX_WEIGHT * (dramaIdxVal / self.NORM_DRAMA_IDX)
        )
        dprint(f"At Bat score {score}/{self.THRESHOLD}")
        dprint(f"probsAddedVal: {probsAddedVal}")
        dprint(f"levIdxVal: {levIdxVal}")
        dprint(f"dramaIdxVal: {dramaIdxVal}")
        dprint(f"win prob complete? {atBat.get("about", {}).get("isComplete", False)}")
        dprint(f"win prob atBatIndex: {atBat.get("atBatIndex", -1)}")
        return score > self.THRESHOLD

    def isABigPlay(self, atBatIndex):
        if stop_event.is_set():
            return

        # TODO: make this smarter. we want to wait for at bat to be done before checking isScoringPlay and isAboveThreshold, but this currently checks at bat finish twice (here + isAboveThreshold())
        atBat = self.getFinishedAtBat(atBatIndex)
        scoringPlay = atBat.get("about", {}).get("isScoringPlay", False)
        return self.isAboveThreshold(atBatIndex) or scoringPlay

    def setWinProbabilities(self):
        winProbabilityList = self.getGameWinProbabilities()
        winProbabilities = []
        for atBat in winProbabilityList:
            winProbabilities.append(self.getWinProbabilityInfo(atBat))
        return winProbabilities

    def findAverages(self):
        atBats = len(self.winProbabilities)
        if (atBats <= 0):
            return
        averageHomeProb = 0.0
        averageAwayProb = 0.0
        averageHomeProbAdded = 0.0
        averageLevIdx = 0.0
        averageDramaIdx = 0.0
        for winProbability in self.winProbabilities:
            averageHomeProb += winProbability.homeTeamWinProbability
            averageAwayProb += winProbability.awayTeamWinProbability
            averageHomeProbAdded += winProbability.homeTeamWinProbabilityAdded
            averageLevIdx += winProbability.leverageIndex
            averageDramaIdx += winProbability.dramaIndex
        averageHomeProb /= atBats
        averageAwayProb /= atBats
        averageHomeProbAdded /= atBats
        averageLevIdx /= atBats
        averageDramaIdx /= atBats
        dprint(f"atBats: {atBats}")
        dprint(f"averageHomeProb: {averageHomeProb}")
        dprint(f"averageAwayProb: {averageAwayProb}")
        dprint(f"averageHomeProbAdded: {averageHomeProbAdded}")
        dprint(f"averageLevIdx: {averageLevIdx}")
        dprint(f"averageDramaIdx: {averageDramaIdx}")

    def findTopTens(self):
        probsAdded = []
        levIdx = []
        dramaIdx = []
        self.scores.clear()
        # loop through all plays and save a tuple of the metric with its at bat index
        for winProb in self.winProbabilities:
            # take abs to get the total top ten probability change plays
            probsAddedVal = abs(winProb.homeTeamWinProbabilityAdded)
            levIdxVal = winProb.leverageIndex
            dramaIdxVal = winProb.dramaIndex
            probsAdded.append((probsAddedVal, winProb.atBatIndex))
            levIdx.append((levIdxVal, winProb.atBatIndex))
            dramaIdx.append((dramaIdxVal, winProb.atBatIndex))
            score = (
                self.PROBS_ADDED_WEIGHT * (probsAddedVal / self.NORM_PROBS_ADDED) 
                + self.LEV_IDX_WEIGHT * (levIdxVal / self.NORM_LEV_IDX) 
                + self.DRAMA_IDX_WEIGHT * (dramaIdxVal / self.NORM_DRAMA_IDX)
            )
            self.scores.append((score, winProb.atBatIndex))

        # probsAdded = [(x * normProbsAddedVal, y) for x, y in probsAdded]
        # levIdx = [(x * normLevIdxVal, y) for x, y in levIdx]
        # dramaIdx = [(x * normDramaIdxVal, y) for x, y in dramaIdx]

        # sort in descending order and save the first ten elements
        self.topTenProbsAdded = heapq.nlargest(10, probsAdded, key=lambda x: x[0])
        self.topTenLevIdx = heapq.nlargest(10, levIdx, key=lambda x: x[0])
        self.topTenDramaIdx = heapq.nlargest(10, dramaIdx, key=lambda x: x[0])
        self.scores = sorted(self.scores, key=lambda x: x[0], reverse=True)
        self.topTenScores = self.scores[:10]
        dprint(f"scores: {self.scores}\n")
        dprint(f"topTenProbsAdded: {self.topTenProbsAdded}\n")
        dprint(f"topTenLevIdx: {self.topTenLevIdx}\n")
        dprint(f"topTenDramaIdx: {self.topTenDramaIdx}\n")
        dprint(f"topTenScores: {self.topTenScores}")
        averageTopTenScore = 0
        for score in self.topTenScores:
            averageTopTenScore += score[0]
        averageTopTenScore /= 10
        dprint()
        print(f"Average top ten score: {averageTopTenScore}")
        print(f"Highest score: {self.topTenScores[0][0]}")
        print(f"Tenth score: {self.topTenScores[-1][0]}")
        inRange = []
        for score in self.scores:
            if (score[0] > self.THRESHOLD):
                inRange.append(score)
        print(f"Plays above the {self.THRESHOLD} threshold: {len(inRange)}")
        
class WinProbabilityInfo():
    def __init__(self, homeProb=0.0, awayProb=0.0, homeProbAdded=0.0, levIdx=0.0, dramaIdx=0.0, atBatIdx=-1):
        self.homeTeamWinProbability = homeProb
        self.awayTeamWinProbability = awayProb
        self.homeTeamWinProbabilityAdded = homeProbAdded
        self.leverageIndex = levIdx
        self.dramaIndex = dramaIdx
        self.atBatIndex = atBatIdx

def main(args):
    cli.getOptions(args)

    # gamePk = 745369
    # gamePk = 823660
    gamePk = 822765
    winProbTest = WinProbability(gamePk)
    winProbTest.findAverages()
    winProbTest.findTopTens()
    print(winProbTest.isAboveThreshold(50))

    # schedule = statsapi.schedule(date="2026-09-06")
    # gamePks = []
    # for game in schedule:
    #     dprint(game)
    #     gamePks.append(game.get("game_id", -1))

    # for gamePk in gamePks:
    #     winProbTest = WinProbability(gamePk)
    #     winProbTest.findAverages()
    #     winProbTest.findTopTens()
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
