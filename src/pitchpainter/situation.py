"""
Situation Class.

Functionality includes everything you would see on a scorebug:
teams, inning, score, pitcher, pitch count, baserunners
"""


class Situation():
    """Handles the contents of every pitch in a game."""

    def __init__(self):
        """Represent the container to output correct data."""
        self.home_team = ""
        self.away_team = ""
        self.home_score = -1
        self.away_score = -1
        self.inning = -1
        self.top = False
        self.balls = -1
        self.strikes = -1
        self.outs = -1
        self.pitcher = ""
        self.pitch_count = 0
        self.baserunners = {1: False, 2: False, 3: False}
        self.baserunners_by_id = {1: -1, 2: -1, 3: -1}
        self.baserunners_at_start_of_at_bat = {1: False, 2: False, 3: False}
        self.play_event_id = -1

    def start_new_game(self, home: str, away: str, pitcher: str = None):
        """Set team names and pitcher, top of the 1st, 0-0 score, 0-0 count, no baserunners, no pitch count."""
        self.home_team = home
        self.away_team = away
        self.home_score = 0
        self.away_score = 0
        self.inning = 1
        self.top = True
        self.balls = 0
        self.strikes = 0
        self.outs = 0
        self.pitcher = ""
        if pitcher is not None:
            self.pitcher = pitcher
        self.pitch_count = 0
        self.baserunners = {1: False, 2: False, 3: False}
        self.baserunners_by_id = {1: -1, 2: -1, 3: -1}

    def set_home_team(self, team: str):
        """Set home team name."""
        self.home_team = team

    def set_away_team(self, team: str):
        """Set away team name."""
        self.away_team = team

    def set_home_score(self, score: int):
        """Set home team score."""
        self.home_score = score

    def set_away_score(self, score: int):
        """Set away team score."""
        self.away_score = score

    def set_play_event_id(self, play_event_id: int):
        """Set current situation's play event id."""
        self.play_event_id = play_event_id

    def set_inning(self, inning: int):
        """Set inning. Clear baserunners if it is a new inning."""
        if inning != self.inning:
            self.baserunners = {1: False, 2: False, 3: False}
        self.inning = inning

    def set_top(self, top: bool):
        """Set top attribute. True for top of an inning, False for bottom of an inning."""
        self.top = top

    def set_balls(self, balls: int):
        """Set current at bat's ball count."""
        self.balls = balls

    def set_strikes(self, strikes: int):
        """Set current at bat's strike count."""
        self.strikes = strikes

    def set_outs(self, outs: int):
        """Set game's outs."""
        self.outs = outs

    def set_pitcher(self, pitcher: str):
        """Set current pitcher on the mound."""
        self.pitcher = pitcher

    def set_pitch_count(self, pitch_count: int):
        """Set current pitcher's pitch count."""
        self.pitch_count = pitch_count

    def set_baserunners(self, baserunners: dict):
        """Set baserunners for current situation."""
        self.baserunners = baserunners

    def set_baserunners_at_start_of_at_bat(self, current_play: dict):
        """Set baserunners at the start of an at bat given the at bat.

        1) Start with the end state - hard save the base and id for all baserunners that aren't the batter at the end
        2) Loop through the runners and add a dict if not batter: key=runner_id, val=list of movements in reverse order
        3) For each entry, find the corresponding and correct starting position for that runner, then hard save it
        """
        if self.outs < 3:
            base_occupied_id = {"1B": -1, "2B": -1, "3B": -1}
            batter_id = current_play.get("matchup", {}).get("batter", {}).get("id", None)

            # 1) get the ids of all bases occupied by non-current batter after the at bat
            post_on_first_id = current_play.get("matchup", {}).get("postOnFirst", {}).get("id", None)
            post_on_second_id = current_play.get("matchup", {}).get("postOnSecond", {}).get("id", None)
            post_on_third_id = current_play.get("matchup", {}).get("postOnThird", {}).get("id", None)
            if post_on_first_id is not None and post_on_first_id != batter_id:
                base_occupied_id["1B"] = post_on_first_id
            if post_on_second_id is not None and post_on_second_id != batter_id:
                base_occupied_id["2B"] = post_on_second_id
            if post_on_third_id is not None and post_on_third_id != batter_id:
                base_occupied_id["3B"] = post_on_third_id

            # 2) get a dict of all non-current batter runners movements during the at bat in reverse order
            runner_movements = {}
            for runner in current_play.get("runners", [])[::-1]:
                runner_id = runner.get("details", {}).get("runner", {}).get("id", None)
                if runner_id is None or runner_id == batter_id:
                    continue
                if runner_id not in runner_movements:
                    runner_movements[runner_id] = []
                runner_movements[runner_id].append(runner.get("movement", {}))

            # 3) reverse engineer where the runners from 1) started the at bat
            for base, runner_id in base_occupied_id.items():
                if runner_id in runner_movements:
                    cur_base = base
                    base_occupied_id[base] = -1
                    for runner_movement in runner_movements[runner_id]:
                        if runner_movement.get("end", None) == cur_base:
                            cur_base = runner_movement.get("start", None)
                    if cur_base in base_occupied_id:
                        base_occupied_id[cur_base] = runner_id
                    runner_movements.pop(runner_id, None)

            # 4) reverse engineer where the other non-batter runners started the at bat given movement data
            for runner_id, cur_runner_movements in runner_movements.items():
                if runner_id is not None:
                    cur_base = None
                    for runner_movement in cur_runner_movements:
                        if cur_base is None or runner_movement.get("end", None) == cur_base:
                            cur_base = runner_movement.get("start", None)
                    if cur_base in base_occupied_id:
                        if base_occupied_id[cur_base] != -1:
                            print("THIS IS AN ERROR!")
                        base_occupied_id[cur_base] = runner_id

            for base, runner_id in base_occupied_id.items():
                if runner_id is not None and runner_id != -1:
                    match base:
                        case "1B":
                            self.baserunners[1] = True
                        case "2B":
                            self.baserunners[2] = True
                        case "3B":
                            self.baserunners[3] = True
                        case _:
                            pass

    def set_baserunners_during_at_bat(self, current_play: dict, play_index):
        """Set baserunners during an at bat.

        Using where a baserunner is and the movement on the play, we can update the baserunner's position.
        """
        bases_occupied = self.baserunners
        runners = current_play.get("runners", {})
        for runner in runners:
            if runner.get("details", {}).get("playIndex", -1) == play_index:
                start_base = runner.get("movement", {}).get("start", "null")
                match start_base:
                    case "1B":
                        bases_occupied[1] = False
                    case "2B":
                        bases_occupied[2] = False
                    case "3B":
                        bases_occupied[3] = False
                    case _:
                        pass
                end_base = runner.get("movement", {}).get("end", "null")
                match end_base:
                    case "1B":
                        bases_occupied[1] = True
                    case "2B":
                        bases_occupied[2] = True
                    case "3B":
                        bases_occupied[3] = True
                    case _:
                        pass

    def set_baserunners_at_end_of_at_bat(self, current_play: dict):
        """Set baserunners at the end of an at bat."""
        bases_occupied = {1: False, 2: False, 3: False}
        if self.outs < 3:
            # At bat is over and the inning continues
            if current_play.get("matchup", {}).get("postOnFirst"):
                bases_occupied[1] = True
            if current_play.get("matchup", {}).get("postOnSecond"):
                bases_occupied[2] = True
            if current_play.get("matchup", {}).get("postOnThird"):
                bases_occupied[3] = True
        self.baserunners = bases_occupied

    def __str__(self):
        """Pretty print return the current situation."""
        return (
            f"Home Team: {self.home_team}\n"
            f"Away Team: {self.away_team}\n"
            f"Home Score: {self.home_score}\n"
            f"Away Score: {self.away_score}\n"
            f"Inning: {self.inning}\n"
            f"Top: {self.top}\n"
            f"Balls: {self.balls}\n"
            f"Strikes: {self.strikes}\n"
            f"Outs: {self.outs}\n"
            f"Pitcher: {self.pitcher}\n"
            f"Pitch Count: {self.pitch_count}\n"
            f"Baserunners: {self.baserunners}"
        )
