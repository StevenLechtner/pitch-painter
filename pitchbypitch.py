import json
from situation import Situation

def drawPitchForTweeting(situation: Situation):

    # Away team row logic
    awayTeam = situation.awayTeam[:3]
    while len(awayTeam) < 3:
        awayTeam += " "
    awayScore = str(situation.awayScore)[:9]
    while len(awayScore) < 9:
        awayScore += " "
    secondBase = '\u25C6    ' if situation.baserunners[2] else '\u25C7    ' # Diamond
    inningHalf = '\u25B2    ' if situation.top else '\u25BC    ' # Triangle
    inning = str(situation.inning)[:5]
    while len(inning) < 5:
        inning += " "
    if situation.top:
        awayRow = f"| {awayTeam} {awayScore}       {secondBase}      {inningHalf}        |"
    else:
        awayRow = f"| {awayTeam} {awayScore}       {secondBase}       {inning}        |"

    # Home team row logic
    homeTeam = situation.homeTeam[:3]
    while len(homeTeam) < 3:
        homeTeam += " "
    homeScore = str(situation.homeScore)[:8]
    while len(homeScore) < 8:
        homeScore += " "
    thirdBase = '\u25C6' if situation.baserunners[3] else '\u25C7' # Diamond
    firstBase = '\u25C6   ' if situation.baserunners[1] else '\u25C7   ' # Diamond
    if situation.top:
        homeRow = f"| {homeTeam}  {homeScore}     {thirdBase}   {firstBase}    {inning}        |"
    else:
        homeRow = f"| {homeTeam}  {homeScore}     {thirdBase}   {firstBase}    {inningHalf}        |"

    # Count row logic
    oneOut = '            \u25CF' if situation.outs >= 1 else '            \u25CB' # Circle
    twoOuts =  '\u25CF' if situation.outs >= 2 else '\u25CB' # Circle
    threeOuts = '\u25CF ' if situation.outs >= 3 else '\u25CB ' # Circle
    balls = str(situation.balls)[:1]
    strikes = str(situation.strikes)[:1]
    while len(strikes) < 4:
        strikes += " "
    countRow = f"|            {oneOut} {twoOuts} {threeOuts}   {balls}-{strikes}      |"

    # Pitcher row logic
    pitcher = situation.pitcher
    if len(pitcher) > 19:
        pitcher = pitcher.split(" ")[1][:18]
    while len(pitcher) < 18:
        pitcher += " "
    pitchCount = str(situation.pitchCount.get(situation.pitcher, 0))[:4]
    while (len(pitchCount) < 4):
        pitchCount += " "
    pitcherRow = f"| {pitcher}        P: {pitchCount}       |"

    # Pretty print all rows into a nice grid of 27 chars per row
    output = ("|─────────────|\n"
              f"{awayRow}\n"
              f"{homeRow}\n"
              f"{countRow}\n"
              "|─────────────|\n"
              f"{pitcherRow}\n"
              "|─────────────|"
    )
    # print("+─────────────────────────+")
    # print(awayRow)
    # print(homeRow)
    # print(countRow)
    # print("|─────────────────────────|")
    # print(pitcherRow)
    # print("+─────────────────────────+\n")
    # print(f"{output}\n")
    #print("│") # TODO: maybe use in the future?
    return output

# FIXME: extra innings look off centered
def drawPitch(situation: Situation):

    # Away team row logic
    awayTeam = situation.awayTeam[:3]
    while len(awayTeam) < 3:
        awayTeam += " "
    awayScore = str(situation.awayScore)[:9]
    while len(awayScore) < 9:
        awayScore += " "
    secondBase = '\u25C6    ' if situation.baserunners[2] else '\u25C7    ' # Diamond
    inningHalf = '\u25B2    ' if situation.top else '\u25BC    ' # Triangle
    inning = str(situation.inning)[:5]
    while len(inning) < 5:
        inning += " "
    if situation.top:
        awayRow = f"|{awayTeam} {awayScore} {secondBase} {inningHalf}|"
    else:
        awayRow = f"|{awayTeam} {awayScore} {secondBase} {inning}|"

    # Home team row logic
    homeTeam = situation.homeTeam[:3]
    while len(homeTeam) < 3:
        homeTeam += " "
    homeScore = str(situation.homeScore)[:8]
    while len(homeScore) < 8:
        homeScore += " "
    thirdBase = '\u25C6' if situation.baserunners[3] else '\u25C7' # Diamond
    firstBase = '\u25C6   ' if situation.baserunners[1] else '\u25C7   ' # Diamond
    if situation.top:
        homeRow = f"|{homeTeam} {homeScore} {thirdBase} {firstBase} {inning}|"
    else:
        homeRow = f"|{homeTeam} {homeScore} {thirdBase} {firstBase} {inningHalf}|"

    # Count row logic
    oneOut = '            \u25CF' if situation.outs >= 1 else '            \u25CB' # Circle
    twoOuts =  '\u25CF' if situation.outs >= 2 else '\u25CB' # Circle
    threeOuts = '\u25CF ' if situation.outs >= 3 else '\u25CB ' # Circle
    balls = str(situation.balls)[:1]
    strikes = str(situation.strikes)[:1]
    while len(strikes) < 4:
        strikes += " "
    countRow = f"|{oneOut} {twoOuts} {threeOuts} {balls}-{strikes}|"

    # Pitcher row logic
    pitcher = situation.pitcher
    if len(pitcher) > 19:
        pitcher = pitcher.split(" ")[1][:18]
    while len(pitcher) < 18:
        pitcher += " "
    pitchCount = str(situation.pitchCount.get(situation.pitcher, 0))[:4]
    while (len(pitchCount) < 4):
        pitchCount += " "
    pitcherRow = f"|{pitcher} P:{pitchCount}|"

    # Pretty print all rows into a nice grid of 27 chars per row
    output = ("+─────────────────────────+\n"
              f"{awayRow}\n"
              f"{homeRow}\n"
              f"{countRow}\n"
              "|─────────────────────────|\n"
              f"{pitcherRow}\n"
              "+─────────────────────────+"
    )
    # print("+─────────────────────────+")
    # print(awayRow)
    # print(homeRow)
    # print(countRow)
    # print("|─────────────────────────|")
    # print(pitcherRow)
    # print("+─────────────────────────+\n")
    # print(f"{output}\n")
    #print("│") # TODO: maybe use in the future?
    return output

def printAllPitchesFromGame(game):
    testOut = ""
    awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    situation = Situation(homeAbbr, awayAbbr, currentPitcher)
    lastDescription = ""
    currentPlay = game["liveData"]["plays"]["currentPlay"]
    plays = game["liveData"]["plays"]["allPlays"]
    playIdx = 0
    i = 0
    while not situation.gameOver:
        currentPlay = game["liveData"]["plays"]["currentPlay"]
        currentPlay = plays[playIdx]
        liveDescription = currentPlay["result"]["description"]
        if (lastDescription != liveDescription):
            lastDescription = liveDescription
            situation.setInning(currentPlay["about"]["inning"])
            situation.setTop(currentPlay["about"]["isTopInning"])
            # situation.setOuts(currentPlay["count"]["outs"])
            situation.setPitcher(currentPlay["matchup"]["pitcher"]["fullName"]) # José Quijada

            # Loop through all play events of current play - print when a pitch is thrown
            for index, playEvent in enumerate(currentPlay["playEvents"]):
                # Ignore if the event is not a pitch
                if not playEvent["isPitch"]:
                    continue

                # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
                if index == len(currentPlay["playEvents"]) - 1:
                    situation.setAwayScore(currentPlay["result"]["awayScore"])
                    situation.setHomeScore(currentPlay["result"]["homeScore"])
                    situation.setOuts(currentPlay["count"]["outs"])
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersFromPlay(currentPlay)

                else:
                    situation.setBalls(playEvent["count"]["balls"])
                    situation.setStrikes(playEvent["count"]["strikes"])
                    situation.setOuts(playEvent["count"]["outs"])

                # Incrememnt pitch count for current pitcher
                pitchCount = situation.pitchCount.get(situation.pitcher, 0)
                pitchCount += 1
                situation.pitchCount[situation.pitcher] = pitchCount

                print(f"{drawPitch(situation)}\n")
                if (situation.balls == 3 and situation.strikes == 2 and situation.outs == 2 and situation.awayScore == 0 and situation.homeScore == 3 and situation.inning == 9):
                    testOut = drawPitch(situation)
                i += 1

            # Check if the result of this at bat finished the game
            if situation.inning >= 9:
                if situation.outs >= 3:
                    if situation.top:
                        if situation.homeScore > situation.awayScore:
                            situation.gameOver = True
                    else:
                        if situation.homeScore != situation.awayScore:
                            situation.gameOver = True
                else:
                    if not situation.top and situation.homeScore > situation.awayScore:
                        situation.gameOver = True
        playIdx += 1

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
    else:
        recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    print()
    print(border)
    print(recap)
    print(border)
    return testOut

def listAllPitchesFromGame(game):
    out = []
    awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    situation = Situation(homeAbbr, awayAbbr, currentPitcher)
    lastDescription = ""
    currentPlay = game["liveData"]["plays"]["currentPlay"]
    plays = game["liveData"]["plays"]["allPlays"]
    playIdx = 0
    i = 0
    while not situation.gameOver:
        currentPlay = game["liveData"]["plays"]["currentPlay"]
        currentPlay = plays[playIdx]
        liveDescription = currentPlay["result"]["description"]
        if (lastDescription != liveDescription):
            lastDescription = liveDescription
            situation.setInning(currentPlay["about"]["inning"])
            situation.setTop(currentPlay["about"]["isTopInning"])
            # situation.setOuts(currentPlay["count"]["outs"])
            situation.setPitcher(currentPlay["matchup"]["pitcher"]["fullName"]) # José Quijada

            # Loop through all play events of current play - print when a pitch is thrown
            for index, playEvent in enumerate(currentPlay["playEvents"]):
                # Ignore if the event is not a pitch
                if not playEvent["isPitch"]:
                    continue

                # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
                if index == len(currentPlay["playEvents"]) - 1:
                    situation.setAwayScore(currentPlay["result"]["awayScore"])
                    situation.setHomeScore(currentPlay["result"]["homeScore"])
                    situation.setOuts(currentPlay["count"]["outs"])
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersFromPlay(currentPlay)

                else:
                    situation.setBalls(playEvent["count"]["balls"])
                    situation.setStrikes(playEvent["count"]["strikes"])
                    situation.setOuts(playEvent["count"]["outs"])

                # Incrememnt pitch count for current pitcher
                pitchCount = situation.pitchCount.get(situation.pitcher, 0)
                pitchCount += 1
                situation.pitchCount[situation.pitcher] = pitchCount

                out.append(drawPitch(situation))
                i += 1

            # Check if the result of this at bat finished the game
            if situation.inning >= 9:
                if situation.outs >= 3:
                    if situation.top:
                        if situation.homeScore > situation.awayScore:
                            situation.gameOver = True
                    else:
                        if situation.homeScore != situation.awayScore:
                            situation.gameOver = True
                else:
                    if not situation.top and situation.homeScore > situation.awayScore:
                        situation.gameOver = True
        playIdx += 1

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
    else:
        recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    out.append("\n")
    out.append(border)
    out.append(recap)
    out.append(border)
    return out

def printLiveGame(game):
    awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    situation = Situation(homeAbbr, awayAbbr, currentPitcher)
    lastDescription = ""
    currentPlay = game["liveData"]["plays"]["currentPlay"]
    while not situation.gameOver:
        currentPlay = game["liveData"]["plays"]["currentPlay"]
        liveDescription = lastDescription
        if (lastDescription == liveDescription):
            lastDescription = liveDescription
            situation.setInning(currentPlay["about"]["inning"])
            situation.setTop(currentPlay["about"]["isTopInning"])
            situation.setPitcher(currentPlay["matchup"]["pitcher"]["fullName"]) # José Quijada

            print(f"{currentPlay["matchup"]["batter"]["fullName"]} now batting.")

            # Loop through all play events of current play - print when a pitch is thrown
            for index, playEvent in enumerate(currentPlay["playEvents"]):
                # Ignore if the event is not a pitch
                if not playEvent["isPitch"]:
                    continue

                # If this is the last pitch of the at bat, then set score, baserunners, and outs, and set balls and strikes to 0
                if index == len(currentPlay["playEvents"]) - 1:
                    situation.setAwayScore(currentPlay["result"]["awayScore"])
                    situation.setHomeScore(currentPlay["result"]["homeScore"])
                    situation.setOuts(currentPlay["count"]["outs"])
                    situation.setBalls(0)
                    situation.setStrikes(0)
                    situation.setBaserunnersFromPlay(currentPlay)

                    print(liveDescription)
                else:
                    situation.setBalls(playEvent["count"]["balls"])
                    situation.setStrikes(playEvent["count"]["strikes"])
                    if playEvent["details"]["isStrike"]:
                        print(f"{playEvent["details"]["description"]} {situation.strikes}.")
                    elif playEvent["details"]["isBall"]:
                        print(f"{playEvent["details"]["description"]} {situation.balls}.")

                # Incrememnt pitch count for current pitcher
                pitchCount = situation.pitchCount.get(situation.pitcher, 0)
                pitchCount += 1
                situation.pitchCount[situation.pitcher] = pitchCount

                print(f"{drawPitch(situation)}\n")

            # Check if the result of this at bat finished the game
            if situation.outs >= 3 and situation.inning >= 9:
                if situation.top:
                    if situation.homeScore > situation.awayScore:
                        situation.gameOver = True
                else:
                    if situation.homeScore != situation.awayScore:
                        situation.gameOver = True

    border = ""
    recap = ""
    if situation.awayScore > situation.homeScore:
        recap = f"|  Final score: {situation.awayScore}-{situation.homeScore}, {situation.awayTeam} over {situation.homeTeam}  |"
    else:
        recap = f"|  Final score: {situation.homeScore}-{situation.awayScore}, {situation.homeTeam} over {situation.awayTeam}  |"
    while len(border) < len(recap):
        border += "─"
    border = "+" + border[1:-1] + "+"
    print()
    print(border)
    print(recap)
    print(border)

def main():
    '''
    Runs the code.
    '''

    '''
    +==============================================+
    |   Testing on all games for a specific date   |
    +==============================================+
    '''
    # gamesList = []
    # schedule = statsapi.get('schedule', {'sportId': 1, 'date': '2025-09-11'})
    # gameList = schedule["dates"][0]["games"]
    # for i in gameList:
    #     gamesList.append(statsapi.get('game', {'gamePk': i["gamePk"]}))
    # print(f"Games for {schedule["dates"][0]["date"]}:")
    # for i in gamesList:
    #     print(f"{i["gameData"]["teams"]["away"]["name"]} @ {i["gameData"]["teams"]["home"]["name"]}")
    # print()

    # game = statsapi.get('game', {'gamePk': 776368})
    # awayTeam = game["gameData"]["teams"]["away"]["name"]
    # homeTeam = game["gameData"]["teams"]["home"]["name"]
    # situation = Situation(homeTeam, awayTeam)
    # drawPitch(situation)
    # print("Home:", homeTeam)
    # print("Away:", awayTeam)
    # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
    # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
    # print("Count:", currentCount)
    # print("Batter:", currentBatter)
    # print("Pitcher:", currentPitcher)



    '''
    +=======================================+
    |   Testing on custom situation input   |
    +=======================================+
    '''
    # print(game["liveData"]["leaders"])
    # situation = Situation("SD", "DET", "Robert Suarez")
    # situation.setPitchCount(25)
    # situation.setHomeScore(3)
    # situation.setBaserunners([1, 2, 3])
    # for i in range(9):
    #     situation.setOuts(random.randint(1, 3))
    #     situation.setBalls(random.randint(0, 3))
    #     situation.setStrikes(random.randint(0, 2))
    #     situation.setInning(i + 1)
    #     drawPitch(situation)
    #     time.sleep(random.randint(1, 2))



    '''
    +============================================================================================================+
    |   Testing on example_out.json (when no wifi so no api calls can happen) - very niche but now's that time   |
    +============================================================================================================+
    '''
    # with open("example_out.json", "r") as f:
    #     game = json.load(f)
    # # print(game)
    # awayTeam = game["gameData"]["teams"]["away"]["name"] # Los Angeles Angels
    # homeTeam = game["gameData"]["teams"]["home"]["name"] # Houston Astros
    # awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    # homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    # situation = Situation(homeAbbr, awayAbbr, currentPitcher)
    # drawPitch(situation)
    # print("Home:", homeTeam)
    # print("Away:", awayTeam)
    # currentCount = game["liveData"]["plays"]["currentPlay"]["count"]
    # currentBatter = game["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["fullName"]
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]
    # print("Count:", currentCount)
    # print("Batter:", currentBatter)
    # print("Pitcher:", currentPitcher)

    '''
    +=========================+
    |   Current Play Output   |
    +=========================+
    '''
    # game = statsapi.get('game', {'gamePk': 776368})
    with open("meadows.json", "r") as f:
    # with open("example_out.json", "r") as f:
        game = json.load(f)
    printAllPitchesFromGame(game)

    '''
    +======================+
    |   Live Play Output   |
    +======================+
    '''
    # game = statsapi.get('game', {'gamePk': 776189})
    # # with open("meadows.json", "r") as f:
    # # # with open("example_out.json", "r") as f:
    # #     game = json.load(f)
    # printLiveGame(game)

if __name__ == '__main__':
    main()
