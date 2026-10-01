class Situation():
    def __init__(self):
        self.homeTeam = ""
        self.awayTeam = ""
        self.homeScore = -1
        self.awayScore = -1
        self.inning = -1
        self.top = False
        self.balls = -1
        self.strikes = -1
        self.outs = -1
        self.pitcher = ""
        self.pitchCount = 0
        self.baserunners = {1: False, 2: False, 3: False}
        self.baserunnersAtStartOfAtBat = {1: False, 2: False, 3: False}
        self.playEventId = -1

    def startNewGame(self, home: str, away: str, pitcher: str = None):
        self.homeTeam = home
        self.awayTeam = away
        self.homeScore = 0
        self.awayScore = 0
        self.inning = 1
        self.top = True
        self.balls = 0
        self.strikes = 0
        self.outs = 0
        self.pitcher = ""
        if pitcher is not None:
            self.pitcher = pitcher
        self.pitchCount = 0
        self.baserunners = {1: False, 2: False, 3: False}
        self.baserunnersById = {1: -1, 2: -1, 3: -1}

    def setHomeTeam(self, team: str):
        self.homeTeam = team
        
    def setAwayTeam(self, team: str):
        self.awayTeam = team

    def setHomeScore(self, score: int):
        self.homeScore = score

    def setAwayScore(self, score: int):
        self.awayScore = score

    def setPlayEventId(self, playEventId: int):
        self.playEventId = playEventId

    def setInning(self, inning: int):
        if inning != self.inning:
            self.baserunners = {1: False, 2: False, 3: False}
        self.inning = inning

    def setTop(self, top: bool):
        self.top = top

    def setBalls(self, balls: int):
        self.balls = balls

    def setStrikes(self, strikes: int):
        self.strikes = strikes

    def setOuts(self, outs: int):
        self.outs = outs

    def setPitcher(self, pitcher: str):
        self.pitcher = pitcher

    def setPitchCount(self, pitchCount: int):
        self.pitchCount = pitchCount

    def setBaserunners(self, baserunners: dict):
            self.baserunners = baserunners

    def setBaserunnersAtStartOfAtBat(self, currentPlay: dict):
        '''
        1) Start with the end state - hard save the base and id for all baserunners that aren't the batter at the end
        2) Loop through the runners and add a dict if not batter: key = runner id, value = list of movements in reverse order
        3) For each entry, find the corresponding and correct starting position for that runner, then hard save it
        '''
        if self.outs < 3:
            baseOccupiedId = {"1B": -1, "2B": -1, "3B": -1}
            batterId = currentPlay.get("matchup", {}).get("batter", {}).get("id", None)

            # 1) get the ids of all bases occupied by non-current batter after the at bat
            postOnFirstId = currentPlay.get("matchup", {}).get("postOnFirst", {}).get("id", None)
            postOnSecondId = currentPlay.get("matchup", {}).get("postOnSecond", {}).get("id", None)
            postOnThirdId = currentPlay.get("matchup", {}).get("postOnThird", {}).get("id", None)
            if postOnFirstId is not None and postOnFirstId != batterId:
                baseOccupiedId["1B"] = postOnFirstId
            if postOnSecondId is not None and postOnSecondId != batterId:
                baseOccupiedId["2B"] = postOnSecondId
            if postOnThirdId is not None and postOnThirdId != batterId:
                baseOccupiedId["3B"] = postOnThirdId
            if (self.awayScore == 8):
                print(baseOccupiedId)

            # 2) get a dict of all non-current batter runners movements during the at bat in reverse order
            runnerMovements = {}
            for runner in currentPlay.get("runners", [])[::-1]:
                runnerId = runner.get("details", {}).get("runner", {}).get("id", None)
                if runnerId is None or runnerId == batterId:
                    continue
                if (self.awayScore == 8):
                    print(runnerId)
                if runnerId not in runnerMovements:
                    runnerMovements[runnerId] = []
                runnerMovements[runnerId].append(runner.get("movement", {}))
            if (self.awayScore == 8):
                print(runnerMovements)

            # 3) reverse engineer where the runners from 1) started the at bat
            for base, runnerId in baseOccupiedId.items():
                if (self.awayScore == 8):
                    print(base, runnerId)
                if runnerId in runnerMovements:
                    curBase = base
                    baseOccupiedId[base] = -1
                    for runnerMovement in runnerMovements[runnerId]:
                        if (self.awayScore == 8):
                                print(runnerMovement)
                        if runnerMovement.get("end", None) == curBase:
                            curBase = runnerMovement.get("start", None)
                            if (self.awayScore == 8):
                                print("curBase: ", curBase)
                    if curBase in baseOccupiedId:
                        baseOccupiedId[curBase] = runnerId
                    runnerMovements.pop(runnerId, None)
            if (self.awayScore == 8):
                print(baseOccupiedId)

            # 4) reverse engineer where the other non-batter runners started the at bat given movement data
            for runnerId, curRunnerMovements in runnerMovements.items():
                if runnerId is not None:
                    curBase = None
                    for runnerMovement in curRunnerMovements:
                        if curBase is None or runnerMovement.get("end", None) == curBase:
                            curBase = runnerMovement.get("start", None)
                    if curBase in baseOccupiedId:
                        if baseOccupiedId[curBase] != -1:
                            print("THIS IS AN ERROR!")
                        baseOccupiedId[curBase] = runnerId
            if (self.awayScore == 8):
                print("end of 4.")
                print(baseOccupiedId)

            for base, runnerId in baseOccupiedId.items():
                if runnerId is not None and runnerId != -1:
                    match base:
                        case "1B":
                            self.baserunners[1] = True
                        case "2B":
                            self.baserunners[2] = True
                        case "3B":
                            self.baserunners[3] = True
                        case _:
                            pass

    def setBaserunnersDuringAtBat(self, currentPlay: dict, playIndex):
        basesOccupied = self.baserunners
        runners = currentPlay.get("runners", {})
        for runner in runners:
            if runner.get("details", {}).get("playIndex", -1) == playIndex:
                startBase = runner.get("movement", {}).get("start", "null")
                match startBase:
                    case "1B":
                        basesOccupied[1] = False
                    case "2B":
                        basesOccupied[2] = False
                    case "3B":
                        basesOccupied[3] = False
                    case _:
                        pass
                endBase = runner.get("movement", {}).get("end", "null")
                match endBase:
                    case "1B":
                        basesOccupied[1] = True
                    case "2B":
                        basesOccupied[2] = True
                    case "3B":
                        basesOccupied[3] = True
                    case _:
                        pass

    def setBaserunnersAtEndOfAtBat(self, currentPlay: dict):
        basesOccupied = {1: False, 2: False, 3: False}
        if self.outs < 3:
            # At bat is over and the inning continues
            if currentPlay.get("matchup", {}).get("postOnFirst"):
                basesOccupied[1] = True
            if currentPlay.get("matchup", {}).get("postOnSecond"):
                basesOccupied[2] = True
            if currentPlay.get("matchup", {}).get("postOnThird"):
                basesOccupied[3] = True
        self.baserunners = basesOccupied

    def __str__(self):
        return f"Home Team: {self.homeTeam}\nAway Team: {self.awayTeam}\nHome Score: {self.homeScore}\nAway Score: {self.awayScore}\nInning: {self.inning}\nTop: {self.top}\nBalls: {self.balls}\nStrikes: {self.strikes}\nOuts: {self.outs}\nPitcher: {self.pitcher}\nPitch Count: {self.pitchCount}\nBaserunners: {self.baserunners}"
