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
        self.pitchCount = {}
        self.baserunners = {1: False, 2: False, 3: False}
        self.gameOver = False

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
        self.pitchCount = {}
        self.baserunners = {1: False, 2: False, 3: False}
        self.gameOver = False

    def setHomeTeam(self, team: str):
        self.homeTeam = team
        
    def setAwayTeam(self, team: str):
        self.awayTeam = team

    def setHomeScore(self, score: int):
        self.homeScore = score

    def setAwayScore(self, score: int):
        self.awayScore = score

    def setInning(self, inning: int):
        # FIXME: Ghost runner logic. Does not work for postseason baseball or pre-ghost runner baseball
        if inning != self.inning:
            self.baserunners = {1: False, 2: False, 3: False}
            # if inning < 10:
            #     self.baserunners = {1: False, 2: False, 3: False}
            # else:
            #     self.baserunners = {1: False, 2: True, 3: False}
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

    def setBaserunnersFromPlay(self, currentPlay: dict, endOfAtBat):
        basesOccupied = self.baserunners
        '''
        | ******************************************************************|
        | Start with the end state - all baserunners at the end become True |
        | Then check movement's end base - all bases here become False      |
        | Then check movement's origin base - all bases here become True    |
        | ******************************************************************|
        '''
        # FIXME: This does not work when a runner does not move during an at bat and the at bat ends the inning. It will show no runners because movement is none and postOn* is none
        # To test: what happens if theres a runner on first and they steal second and then the inning ends?
        if not endOfAtBat and self.outs < 3:
            # First we check the end state of the baserunners for this at bat
            # All baserunners found become True
            if currentPlay.get("matchup", {}).get("postOnFirst"):
                basesOccupied[1] = True
            if currentPlay.get("matchup", {}).get("postOnSecond"):
                basesOccupied[2] = True
            if currentPlay.get("matchup", {}).get("postOnThird"):
                basesOccupied[3] = True

            # Next we check the at bat runners' movement end base
            # All baserunners found become False
            for runner in currentPlay.get("runners", {}):
                base = runner.get("movement", {}).get("end", "null")
                match base:
                    case "1B":
                        basesOccupied[1] = False
                    case "2B":
                        basesOccupied[2] = False
                    case "3B":
                        basesOccupied[3] = False
                    case _:
                        pass

            # Finally we check the at bat runners' movement origin base
            # All baserunners found become True
            for runner in currentPlay.get("runners", {}):
                base = runner.get("movement", {}).get("originBase", "null")
                match base:
                    case "1B":
                        basesOccupied[1] = True
                    case "2B":
                        basesOccupied[2] = True
                    case "3B":
                        basesOccupied[3] = True
                    case _:
                        pass
        else:
            basesOccupied[1] = False
            basesOccupied[2] = False
            basesOccupied[3] = False
            if self.outs < 3:
                # At bat is over and the inning continues
                if currentPlay.get("matchup", {}).get("postOnFirst"):
                    basesOccupied[1] = True
                if currentPlay.get("matchup", {}).get("postOnSecond"):
                    basesOccupied[2] = True
                if currentPlay.get("matchup", {}).get("postOnThird"):
                    basesOccupied[3] = True

        self.baserunners = basesOccupied

    def processAtBatFinished(self, atBatToProcess):
        self.setAwayScore(atBatToProcess.get("result", {}).get("awayScore", -1))
        self.setHomeScore(atBatToProcess.get("result", {}).get("homeScore", -1))
        self.setOuts(atBatToProcess.get("count", {}).get("outs", -1))
        self.setBalls(0)
        self.setStrikes(0)
        self.setBaserunnersFromPlay(atBatToProcess, True)
        # Check if the result of this at bat finished the game
        if self.inning >= 9:
            if self.outs >= 3:
                if self.top:
                    if self.homeScore > self.awayScore:
                        self.gameOver = True
                else:
                    if self.homeScore != self.awayScore:
                        self.gameOver = True
            else:
                if not self.top and self.homeScore > self.awayScore:
                    self.gameOver = True
        # Half inning is over but game is not done yet - set outs to 0
        if not self.gameOver and self.outs == 3:
            self.setOuts(0)

    def __str__(self):
        return f"Home Team: {self.homeTeam}\nAway Team: {self.awayTeam}\nHome Score: {self.homeScore}\nAway Score: {self.awayScore}\nInning: {self.inning}\nTop: {self.top}\nBalls: {self.balls}\nStrikes: {self.strikes}\nOuts: {self.outs}\nPitcher: {self.pitcher}\nPitch Count: {self.pitchCount}\nBaserunners: {self.baserunners}\nGame Over: {self.gameOver}"
