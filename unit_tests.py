from io import StringIO

import json
import pitchbypitch
import random
import statsapi
import sys
import time
import unittest

class TestPrint(unittest.TestCase):
    def save_prints(self, situation):
        # output = StringIO()
        # sys.stdout = output
        out = pitchbypitch.drawPitch(situation)
        # sys.stdout = sys.__stdout__
        out = out.strip().split('\n')
        for line in out:
            self.assertEqual(len(line), 27)

    def test_out_row_len(self):
        with open("example_out.json", "r") as f:
            game = json.load(f)
        awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
        homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
        currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
        situation = pitchbypitch.Situation(homeAbbr, awayAbbr, currentPitcher)
        self.save_prints(situation)
        situation.setPitcher("")
        situation.setAwayTeam("")
        self.save_prints(situation)
        situation.setAwayScore(0)
        self.save_prints(situation)
        situation.setAwayScore(10)
        self.save_prints(situation)
        situation.setAwayScore(10000000099345678991213213123231)
        self.save_prints(situation)

if __name__ == '__main__':
    unittest.main()
