"""Use MLB's win probability added, leverage index, and drama index of every at bat to find big plays of a game."""


import heapq
import json
import sys
import threading
from dataclasses import dataclass
import requests
import statsapi
from pitchpainter import cli
from pitchpainter.print_util import dprint

stop_event = threading.Event()


def stop():
    """Stop checking win probabilities."""
    dprint("win_probability stop_event is True")
    stop_event.set()


def start():
    """Start checking win probabilities."""
    dprint("win_probability stop_event is False")
    stop_event.clear()


class WinProbability():
    """Get win probabilities of an at bat and determine if it is a big play."""

    # score weights
    NORM_PROBS_ADDED = 25
    NORM_LEV_IDX = 2.5
    NORM_DRAMA_IDX = 150
    PROBS_ADDED_WEIGHT = 0.7
    LEV_IDX_WEIGHT = 0.15
    DRAMA_IDX_WEIGHT = 0.15
    THRESHOLD = 0.375

    def __init__(self, game_pk=None, _filepath=None):
        """Initialize this object with win probabilities."""
        self.game_pk = -1 if game_pk is None else game_pk
        self.filepath = _filepath
        self.win_probabilities: list[WinProbabilityInfo] = self.set_win_probabilities()
        # Top ten: List of tuples (x, y) where x is the metric and y is the at bat index
        self.top_ten_probs_added = []
        self.top_ten_lev_idx = []
        self.top_ten_drama_idx = []
        self.scores = []

    def get_game_win_probabilities(self):
        """Set all at bats win probabilites from filepath if found; from the server by gamePk if not."""
        if stop_event.is_set():
            return []

        win_probability_list = []

        # path to a win probability local file is provided. Use first, but check server if this fails
        if self.filepath:
            with open(self.filepath, "r", encoding="utf-8") as f:
                win_probability_list = json.load(f)
                if win_probability_list:
                    return win_probability_list

        # No path is provided. Get win probabilities from the server using the gamePk
        # Try HTTP GET request up to three times before failing
        for attempt in range(3):
            if stop_event.is_set():
                return []
            try:
                win_probability_list = statsapi.get('game_winProbability', {'gamePk': self.game_pk})
                if win_probability_list:
                    return win_probability_list
            except requests.exceptions.RequestException as e:
                print(
                    f"https://statsapi.mlb.com/api/v1.1/game/{self.game_pk}/winProbability "
                    f"request failed (attempt {attempt + 1}/3): {e}"
                )
                if attempt < 2:
                    if stop_event.wait(1):
                        return []
                else:
                    print(f"Failed to retrieve win probability (game_pk={self.game_pk}) GET request after 3 attempts.")
                    win_probability_list.clear()
        return []

    def at_bat_finished(self, at_bat_index: int):
        """Get the win probability weights from the end of this at bat.

        Wait for the at bat to end by checking if there is a new at bat after this, or the game is over.
        Note that checking game over here is checking of one team's win probability is 100%.
        """
        if not self.win_probabilities:
            self.set_win_probabilities()
            if not self.win_probabilities:
                dprint("Failed to find win probabilities!")
                return False
        # return of there is already a new at bat or the game is over
        latest_at_bat_index = self.win_probabilities[-1].at_bat_index
        if (
            latest_at_bat_index > at_bat_index
            or (self.win_probabilities[-1].home_team_win_probability >= 100
                or self.win_probabilities[-1].away_team_win_probability >= 100)
        ):
            return True

        # we need to wait for at bat to complete to get finalized at bat win probability numbers
        # check if the next at_bat_index is present
        # if not, check if a win probability is 100% (indicates game over)
        win_probability_list = []
        # TODO: don't make this an "infinite" loop. Check for a max of 5(ish) minutes?
        # Determine how long it takes to be 100% sure that the values are updated
        # TODO: Additional check - see if any values are different (win prob, drama, lev) - different indicates
        # they're updated, but they could be updated to the same...
        while not stop_event.is_set():
            win_probability_list = self.get_game_win_probabilities()
            if not win_probability_list:
                # win probabilities list is empty!
                if stop_event.wait(5):
                    break
                continue
            latest_at_bat = win_probability_list[-1]
            latest_at_bat_index = latest_at_bat.get("atBatIndex", -1)
            # return if there is a new at bat or the game is over
            if (
                latest_at_bat_index > at_bat_index
                or (latest_at_bat.get("homeTeamWinProbability", -1) >= 100
                    or latest_at_bat.get("awayTeamWinProbability", -1) >= 100)
            ):
                return True
            if latest_at_bat_index < at_bat_index:
                # error check: this at bat has not even happened yet
                dprint(f"Win probability at bat has not happened yet! {at_bat_index} < {latest_at_bat_index}")
                return False
            # at bat is not yet complete
            if stop_event.wait(5):
                break
        return False

    def get_win_probability_info(self, at_bat):
        """Convert at bat's win probability weights to a WinProbabilityInfo object."""
        home_prob = at_bat.get("homeTeamWinProbability", 0.0)
        away_prob = at_bat.get("awayTeamWinProbability", 0.0)
        home_prob_added = at_bat.get("homeTeamWinProbabilityAdded", 0.0)
        lev_idx = at_bat.get("leverageIndex", 0.0)
        drama_idx = at_bat.get("dramaIndex", 0.0)
        at_bat_idx = at_bat.get("atBatIndex", 0.0)
        is_scoring_play = at_bat.get("about", {}).get("isScoringPlay", False)
        is_complete = at_bat.get("about", {}).get("isComplete", False)
        return WinProbabilityInfo(home_prob,
                                  away_prob,
                                  home_prob_added,
                                  lev_idx,
                                  drama_idx,
                                  at_bat_idx,
                                  is_scoring_play,
                                  is_complete)

    def is_above_threshold(self, at_bat_index: int):
        """Check if this at bat's score is above the threshold to trigger a big play.

        Use the atBatIndex to get the at bat,
        wait for the at bat to be finished (win probability weights finalized),
        calculate the score using the weights,
        and return True if the score is above the THRESHOLD, False otherwise.
        """
        if at_bat_index < 0:
            return False

        if not self.at_bat_finished(at_bat_index):
            return False

        # return False if at_bat_index is out of range on possible at bats in win_probabilities
        if at_bat_index >= len(self.win_probabilities) or at_bat_index < 0:
            return False

        win_prob = self.win_probabilities[at_bat_index]
        probs_added_val = abs(win_prob.home_team_win_probability_added)
        lev_idx_val = win_prob.leverage_index
        drama_idx_val = win_prob.drama_index
        score = (
            self.PROBS_ADDED_WEIGHT * (probs_added_val / self.NORM_PROBS_ADDED)
            + self.LEV_IDX_WEIGHT * (lev_idx_val / self.NORM_LEV_IDX)
            + self.DRAMA_IDX_WEIGHT * (drama_idx_val / self.NORM_DRAMA_IDX)
        )
        dprint(f"At Bat score {score}/{self.THRESHOLD}")
        dprint(f"probsAddedVal: {probs_added_val}")
        dprint(f"levIdxVal: {lev_idx_val}")
        dprint(f"dramaIdxVal: {drama_idx_val}")
        dprint(f"win prob complete? {win_prob.is_complete}")
        dprint(f"win prob atBatIndex: {win_prob.at_bat_index}")
        return score > self.THRESHOLD

    def is_a_big_play(self, at_bat_index: int):
        """Return True if this at bat is above the THRESHOLD or is a scoring play. False otherise."""
        if stop_event.is_set():
            return False

        # TODO: make this smarter. we want to wait for at bat to be done before checking isScoringPlay and
        # isAboveThreshold, but this currently checks at bat finish twice (here + isAboveThreshold())
        if at_bat_index < 0:
            return False

        if not self.at_bat_finished(at_bat_index):
            return False

        # return False if at_bat_index is out of range on possible at bats in win_probabilities
        if at_bat_index >= len(self.win_probabilities) or at_bat_index < 0:
            return False

        scoring_play = self.win_probabilities[at_bat_index].is_scoring_play
        return self.is_above_threshold(at_bat_index) or scoring_play

    def set_win_probabilities(self):
        """Configure each finished at bat's win probabilities as a WinProbabilityInfo object."""
        dprint(self.filepath)
        win_probability_list = self.get_game_win_probabilities()
        win_probabilities = []
        for at_bat in win_probability_list:
            win_probabilities.append(self.get_win_probability_info(at_bat))
        return win_probabilities

    # TODO: remove?
    def find_averages(self):
        """Find the average score of each at bat."""
        at_bats = len(self.win_probabilities)
        if at_bats <= 0:
            return
        average_home_prob = 0.0
        average_away_prob = 0.0
        average_home_prob_added = 0.0
        average_lev_idx = 0.0
        average_drama_idx = 0.0
        for win_probability in self.win_probabilities:
            average_home_prob += win_probability.home_team_win_probability
            average_away_prob += win_probability.away_team_win_probability
            average_home_prob_added += win_probability.home_team_win_probability_added
            average_lev_idx += win_probability.leverage_index
            average_drama_idx += win_probability.drama_index
        average_home_prob /= at_bats
        average_away_prob /= at_bats
        average_home_prob_added /= at_bats
        average_lev_idx /= at_bats
        average_drama_idx /= at_bats
        dprint(f"atBats: {at_bats}")
        dprint(f"averageHomeProb: {average_home_prob}")
        dprint(f"averageAwayProb: {average_away_prob}")
        dprint(f"averageHomeProbAdded: {average_home_prob_added}")
        dprint(f"averageLevIdx: {average_lev_idx}")
        dprint(f"averageDramaIdx: {average_drama_idx}")

    # TODO: remove?
    def find_top_tens(self):
        """Find the top ten scores of a game."""
        probs_added = []
        lev_idx = []
        drama_idx = []
        self.scores.clear()
        # loop through all plays and save a tuple of the metric with its at bat index
        for win_prob in self.win_probabilities:
            # take abs to get the total top ten probability change plays
            probs_added_val = abs(win_prob.home_team_win_probability_added)
            lev_idx_val = win_prob.leverage_index
            drama_idx_val = win_prob.drama_index
            probs_added.append((probs_added_val, win_prob.at_bat_index))
            lev_idx.append((lev_idx_val, win_prob.at_bat_index))
            drama_idx.append((drama_idx_val, win_prob.at_bat_index))
            score = (
                self.PROBS_ADDED_WEIGHT * (probs_added_val / self.NORM_PROBS_ADDED)
                + self.LEV_IDX_WEIGHT * (lev_idx_val / self.NORM_LEV_IDX)
                + self.DRAMA_IDX_WEIGHT * (drama_idx_val / self.NORM_DRAMA_IDX)
            )
            self.scores.append((score, win_prob.at_bat_index))

        # probsAdded = [(x * normProbsAddedVal, y) for x, y in probsAdded]
        # levIdx = [(x * normLevIdxVal, y) for x, y in levIdx]
        # dramaIdx = [(x * normDramaIdxVal, y) for x, y in dramaIdx]

        # sort in descending order and save the first ten elements
        self.top_ten_probs_added = heapq.nlargest(10, probs_added, key=lambda x: x[0])
        self.top_ten_lev_idx = heapq.nlargest(10, lev_idx, key=lambda x: x[0])
        self.top_ten_drama_idx = heapq.nlargest(10, drama_idx, key=lambda x: x[0])
        self.scores = sorted(self.scores, key=lambda x: x[0], reverse=True)
        top_ten_scores = self.scores[:10]
        dprint(f"scores: {self.scores}\n")
        dprint(f"topTenProbsAdded: {self.top_ten_probs_added}\n")
        dprint(f"topTenLevIdx: {self.top_ten_lev_idx}\n")
        dprint(f"topTenDramaIdx: {self.top_ten_drama_idx}\n")
        dprint(f"topTenScores: {top_ten_scores}")
        average_top_ten_score = 0
        for score in top_ten_scores:
            average_top_ten_score += score[0]
        average_top_ten_score /= 10
        dprint()
        print(f"Average top ten score: {average_top_ten_score}")
        print(f"Highest score: {top_ten_scores[0][0]}")
        print(f"Tenth score: {top_ten_scores[-1][0]}")
        in_range = []
        for score in self.scores:
            if score[0] > self.THRESHOLD:
                in_range.append(score)
        print(f"Plays above the {self.THRESHOLD} threshold: {len(in_range)}")


# pylint: disable=too-many-instance-attributes
# one too many attributes is fine. is_complete is only used for debug prints but it is still helpful
@dataclass
class WinProbabilityInfo:
    """Save win probability weights and at bat index. Weights 0.0 and index -1 if not present."""

    home_team_win_probability: float = 0.0
    away_team_win_probability: float = 0.0
    home_team_win_probability_added: float = 0.0
    leverage_index: float = 0.0
    drama_index: float = 0.0
    at_bat_index: int = -1
    is_scoring_play: bool = False
    is_complete: bool = False


# TODO: Remove this?
def main():
    """Test this file."""
    cli.get_options(sys.argv[1:])

    # gamePk = 745369
    # gamePk = 823660
    game_pk = 822765
    win_prob_test = WinProbability(game_pk)
    win_prob_test.find_averages()
    win_prob_test.find_top_tens()
    print(win_prob_test.is_above_threshold(50))

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
    main()
