"""
Situation Class.

Functionality includes everything you would see on a scorebug:
teams, inning, score, pitcher, pitch count, baserunners
"""


class Situation():
    """Handles the contents of every pitch in a game."""

    # pylint: disable=too-many-instance-attributes
    # This class acts as a data interpreter. 15 attributes is okay here.
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
        """Set inning attribute."""
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
        if self.outs >= 3 or self.outs < 0:
            return

        batter_id = current_play.get("matchup", {}).get("batter", {}).get("id", None)

        # 1) get the ids of all bases occupied by non-current batter after the at bat
        base_occupied_id = self.__get_runners_post_at_bat_position(current_play, batter_id)

        # 2) get a dict of all non-current batter runners movements during the at bat in reverse order
        runner_movements = self.__get_runners_reverse_movement(current_play, batter_id)

        # 3) use runner_movements (2) to reverse engineer where the non-batter runners (1) started the at bat
        self.__trace_runners_to_start_at_bat_position(base_occupied_id, runner_movements)

        # 4) reverse engineer where the other non-batter runners started the at bat given movement data
        self.__trace_additional_runners_to_start_at_bat_position(base_occupied_id, runner_movements)

        # 5) translate base_occupied_id (3+4) to Situation baserunners attribute to set baserunners at start of at bat
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

    @staticmethod
    def __get_runners_post_at_bat_position(current_play: dict, batter_id):
        """Get the position of every non-batter runner at the end of the at bat. Return the result."""
        base_occupied_id = {"1B": -1, "2B": -1, "3B": -1}
        post_on_first_id = current_play.get("matchup", {}).get("postOnFirst", {}).get("id", None)
        post_on_second_id = current_play.get("matchup", {}).get("postOnSecond", {}).get("id", None)
        post_on_third_id = current_play.get("matchup", {}).get("postOnThird", {}).get("id", None)
        if post_on_first_id is not None and post_on_first_id != batter_id:
            base_occupied_id["1B"] = post_on_first_id
        if post_on_second_id is not None and post_on_second_id != batter_id:
            base_occupied_id["2B"] = post_on_second_id
        if post_on_third_id is not None and post_on_third_id != batter_id:
            base_occupied_id["3B"] = post_on_third_id
        return base_occupied_id

    @staticmethod
    def __get_runners_reverse_movement(current_play: dict, batter_id):
        """Get the movement of every non-batter runner during the at bat in reverse order. Return the result."""
        runner_movements = {}
        for runner in current_play.get("runners", [])[::-1]:
            runner_id = runner.get("details", {}).get("runner", {}).get("id", None)
            if runner_id is None or runner_id == batter_id:
                continue
            if runner_id not in runner_movements:
                runner_movements[runner_id] = []
            runner_movements[runner_id].append(runner.get("movement", {}))
        return runner_movements

    @staticmethod
    def __trace_runners_to_start_at_bat_position(base_occupied_id: dict, runner_movements: dict):
        """Use runner movements to find the runner's initial position and save it to base_occupied_id."""
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

    @staticmethod
    def __trace_additional_runners_to_start_at_bat_position(base_occupied_id: dict, runner_movements: dict):
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

    # pylint: disable=too-many-locals
    # It's okay that this function has many local variables. They are all small and useful.
    def draw_pitch(self, alt_text=False):
        """Draw a pitch given the situation with spacing used for stdout and image uploading for Threads posts.

        Use alt text spacing if specified for a Threads post's alt text section.<br>
        Returns the output as a string.<br><br>
        Symbols table:<br>
        \u25C6=Filled diamond (base is occupied)<br>
        \u25C7=Emtpy diamond (base is empty)<br>
        \u25B2=Triangle up (top of the inning)<br>
        \u25BC=Triangle down (bottom of the inning)<br>
        \u25CF=Filled circle (out)<br>
        \u25CB=Empty circle (no out)
        """
        # Shared data preparation and padding
        away_team = self.away_team[:3].ljust(3)
        away_score = str(self.away_score)[:9].ljust(9)
        home_team = self.home_team[:3].ljust(3)
        home_score = str(self.home_score)[:8].ljust(8)
        inning = str(self.inning)[:5].ljust(5)
        balls = str(self.balls)[:1]
        strikes = str(self.strikes)[:1].ljust(4)
        pitcher = self.pitcher
        if len(pitcher) > 19:
            pitcher = pitcher.split(" ")[1][:18]  # TODO: test this
        pitcher = pitcher.ljust(18)
        pitch_count = str(self.pitch_count)[:4].ljust(4)

        if not alt_text:
            # pretty print stdout/image text layout
            second_base = '\u25C6    ' if self.baserunners[2] else '\u25C7    '
            third_base = '\u25C6' if self.baserunners[3] else '\u25C7'
            first_base = '\u25C6   ' if self.baserunners[1] else '\u25C7   '
            inning_half = '\u25B2    ' if self.top else '\u25BC    '
            away_row = f"|{away_team} {away_score} {second_base} {inning_half if self.top else inning}|"
            home_row = f"|{home_team} {home_score} {third_base} {first_base} {inning if self.top else inning_half}|"
            one_out = f'            {"\u25CF" if self.outs >= 1 else "\u25CB"}'
            two_outs = '\u25CF' if self.outs >= 2 else '\u25CB'
            three_outs = '\u25CF ' if self.outs >= 3 else '\u25CB '
            count_row = f"|{one_out} {two_outs} {three_outs} {balls}-{strikes}|"
            pitcher_row = f"|{pitcher} P:{pitch_count}|"
            border = "+─────────────────────────+"
            divider = "|─────────────────────────|"
        else:
            # Threads alt text/direct post as text instead of image layout
            second_base = '\u25C6    ' if self.baserunners[2] else '\u25C7    '
            third_base = '\u25C6' if self.baserunners[3] else '\u25C7'
            first_base = '\u25C6   ' if self.baserunners[1] else '\u25C7   '
            inning_half = '\u25B2    ' if self.top else '\u25BC    '
            away_row = (
                f"| {away_team} {away_score}       {second_base}       "
                f"{inning_half if self.top else inning}        |"
            )
            home_row = (
                f"| {home_team}  {home_score}     {third_base}   {first_base}    "
                f"{inning if self.top else inning_half}        |"
            )
            one_out = f'            {"\u25CF" if self.outs >= 1 else "\u25CB"}'
            two_outs = '\u25CF' if self.outs >= 2 else '\u25CB'
            three_outs = '\u25CF ' if self.outs >= 3 else '\u25CB '
            count_row = f"|            {one_out} {two_outs} {three_outs}   {balls}-{strikes}      |"
            pitcher_row = f"| {pitcher}        P: {pitch_count}       |"
            border = "+─────────────+"
            divider = "|─────────────|"

        # Pretty print all rows into a nice grid
        output = (
            f"{border}\n"
            f"{away_row}\n"
            f"{home_row}\n"
            f"{count_row}\n"
            f"{divider}\n"
            f"{pitcher_row}\n"
            f"{border}"
        )
        return output

    def draw_pitch_with_score(self, _away_score, _home_score, alt_text=False):
        """Draw a pitch with a score update added on run(s) scored. Use alt text spacing if specified."""
        score_spacing = 12 if alt_text else 8
        border = "+──────+" if alt_text else "+────────────+"
        away_team = self.away_team[:3].ljust(3)
        away_score = str(_away_score)[:9].ljust(score_spacing)
        home_team = self.home_team[:3].ljust(3)
        home_score = str(_home_score)[:8].ljust(score_spacing)
        away_row = f"|{away_team} {away_score}|"
        home_row = f"|{home_team} {home_score}|"
        if alt_text:
            away_row = f"| {away_team}  {away_score}|"
            home_row = f"| {home_team}  {home_score}|"

        # Pretty print all rows into a nice grid
        output = (
            f"{border}\n"
            "|Score update|\n"
            f"{away_row}\n"
            f"{home_row}\n"
            f"{border}"
        )
        pitch_text = self.draw_pitch(alt_text)
        return pitch_text + "\n" + output

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
