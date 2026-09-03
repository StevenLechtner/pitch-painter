import cli
import heapq
import statsapi
import sys
from print_util import dprint

class WinProbability():
    def __init__(self, gamePk=None):
        self.gamePk = -1 if gamePk is None else gamePk
        self.winProbabilities: list[WinProbabilityInfo] = self.setWinProbabilities() # List of WinProbabilityInfo
        # Top ten: List of tuples (x, y) where x is the metric and y is the at bat index
        self.topTenProbsAdded = []
        self.topTenLevIdx = []
        self.topTenDramaIdx = []
        self.scores = []
        self.topTenScores = []

    def setWinProbabilities(self):
        winProbabilityList = statsapi.get('game_winProbability', {'gamePk': self.gamePk})
        winProbabilities = []
        for atBat in winProbabilityList:
            homeProb = atBat.get("homeTeamWinProbability", 0.0)
            awayProb = atBat.get("awayTeamWinProbability", 0.0)
            homeProbAdded = atBat.get("homeTeamWinProbabilityAdded", 0.0)
            levIdx = atBat.get("leverageIndex", 0.0)
            dramaIdx = atBat.get("dramaIndex", 0.0)
            atBatIdx = atBat.get("atBatIndex", 0.0)
            winProbabilities.append(WinProbabilityInfo(homeProb, awayProb, homeProbAdded, levIdx, dramaIdx, atBatIdx))
        return winProbabilities

    def findAverages(self):
        averageHomeProb = 0.0
        averageAwayProb = 0.0
        averageHomeProbAdded = 0.0
        averageLevIdx = 0.0
        averageDramaIdx = 0.0
        atBats = len(self.winProbabilities)
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
        scores = []
        # loop through all plays and save a tuple of the metric with its at bat index
        for winProb in self.winProbabilities:
            # take abs to get the total top ten probability change plays
            normProbsAdded = abs(winProb.homeTeamWinProbabilityAdded) / 25
            normLevIdx = winProb.leverageIndex / 2.5
            normDramaIdx = winProb.dramaIndex / 150
            probsAdded.append((normProbsAdded, winProb.atBatIndex))
            levIdx.append((normLevIdx, winProb.atBatIndex))
            dramaIdx.append((normDramaIdx, winProb.atBatIndex))
            score = 0.7 * normProbsAdded + 0.15 * normLevIdx + 0.15 * normDramaIdx
            scores.append((score, winProb.atBatIndex))

        # sort in descending order and save the first ten elements
        self.topTenProbsAdded = heapq.nlargest(10, probsAdded, key=lambda x: x[0])
        self.topTenLevIdx = heapq.nlargest(10, levIdx, key=lambda x: x[0])
        self.topTenDramaIdx = heapq.nlargest(10, dramaIdx, key=lambda x: x[0])
        self.scores = sorted(scores, key=lambda x: x[0], reverse=True)
        self.topTenScores = self.scores[:10]
        print(f"scores: {self.scores}")
        print(f"topTenProbsAdded: {self.topTenProbsAdded}")
        print(f"topTenLevIdx: {self.topTenLevIdx}")
        print(f"topTenDramaIdx: {self.topTenDramaIdx}")
        print(f"topTenScores: {self.topTenScores}")

    def normalizeTopTens(self):
        for elt in self.topTenProbsAdded:
            elt[0] /= 100
        print(f"normTopTenProbsAdded: {self.topTenProbsAdded}")
        
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

    winProbTest = WinProbability(823660)
    #winProbTest = WinProbability(745369)
    winProbTest.findAverages()
    winProbTest.findTopTens()
    #winProbTest.normalizeTopTens()
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
