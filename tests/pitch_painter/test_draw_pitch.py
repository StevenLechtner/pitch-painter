import copy
from pitchpainter.situation import Situation


meadows_situation = Situation()
meadows_situation.set_away_team("DET")
meadows_situation.set_away_score(0)
meadows_situation.set_home_team("SD")
meadows_situation.set_home_score(3)
meadows_situation.set_inning(9)
meadows_situation.set_baserunners({1: True, 2: True, 3: True})
meadows_situation.set_top(True)
meadows_situation.set_balls(3)
meadows_situation.set_strikes(2)
meadows_situation.set_outs(2)
meadows_situation.set_pitcher("Robert Suarez")
meadows_situation.set_pitch_count(25)


def test_draw_pitch():
    """Test that textToPNG successfully generates a png from text."""
    situation = copy.deepcopy(meadows_situation)
    correct_out = (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    )
    out = situation.draw_pitch()
    assert out == correct_out


def test_draw_pitch_with_score():
    situation = copy.deepcopy(meadows_situation)
    correct_out = (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+\n"
        "+────────────+\n"
        "|Score update|\n"
        "|DET 4       |\n"
        "|SD  3       |\n"
        "+────────────+"
    )
    out = situation.draw_pitch_with_score(4, 3)
    assert out == correct_out


def test_draw_pitch_alt_text():
    situation = copy.deepcopy(meadows_situation)
    correct_out = (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    )
    out = situation.draw_pitch(alt_text=True)
    assert out == correct_out


def test_draw_pitch_with_score_alt_text():
    situation = copy.deepcopy(meadows_situation)
    correct_out = (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+\n"
        "+──────+\n"
        "|Score update|\n"
        "| DET  4           |\n"
        "| SD   3           |\n"
        "+──────+"
    )
    out = situation.draw_pitch_with_score(4, 3, alt_text=True)
    assert out == correct_out


def test_draw_all_types_of_pitches():
    situation = copy.deepcopy(meadows_situation)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_outs(0)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ○ ○ ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ○ ○ ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_outs(1)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ○ ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ○ ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_outs(2)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_balls(0)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  0-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    0-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_balls(1)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  1-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    1-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_balls(2)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  2-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    2-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_balls(3)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_strikes(0)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-0   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-0         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_strikes(1)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-1   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-1         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_strikes(2)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: False, 2: False, 3: False})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◇     ▲    |\n"
        "|SD  3        ◇ ◇    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◇           ▲            |\n"
        "| SD   3            ◇   ◇       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: True, 2: False, 3: False})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◇     ▲    |\n"
        "|SD  3        ◇ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◇           ▲            |\n"
        "| SD   3            ◇   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: True, 2: True, 3: False})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◇ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◇   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: True, 2: False, 3: True})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◇     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◇           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: False, 2: True, 3: True})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◇    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◇       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_baserunners({1: True, 2: True, 3: True})
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_away_team("SD")
    situation.set_home_team("DET")
    assert (
        "+─────────────────────────+\n"
        "|SD  0         ◆     ▲    |\n"
        "|DET 3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| SD  0               ◆           ▲            |\n"
        "| DET  3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_away_score(10)
    situation.set_home_score(10)
    assert (
        "+─────────────────────────+\n"
        "|SD  10        ◆     ▲    |\n"
        "|DET 10       ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| SD  10              ◆           ▲            |\n"
        "| DET  10           ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_away_team("DET")
    situation.set_home_team("SD")
    assert (
        "+─────────────────────────+\n"
        "|DET 10        ◆     ▲    |\n"
        "|SD  10       ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 10              ◆           ▲            |\n"
        "| SD   10           ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_away_score(0)
    situation.set_home_score(3)
    situation.set_top(False)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     9    |\n"
        "|SD  3        ◆ ◆    ▼    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           9            |\n"
        "| SD   3            ◆   ◆       ▼            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_top(True)
    situation.set_pitch_count(1)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:1   |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 1          |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_pitch_count(100)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:100 |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 100        |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_pitch_count(25)
    situation.set_pitcher("Short Name")
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Short Name         P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Short Name                P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_pitcher("Abcdefghijklmnopqrstuvwxyz LastName")
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|LastName           P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| LastName                  P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_pitcher("FirstName Abcdefghijklmnopqrstuvwxyz")
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Abcdefghijklmnopqr P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Abcdefghijklmnopqr        P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_pitcher("Robert Suarez")
    situation.set_inning(12)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    12   |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           ▲            |\n"
        "| SD   3            ◆   ◆       12           |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation.set_top(False)
    assert (
        "+─────────────────────────+\n"
        "|DET 0         ◆     12   |\n"
        "|SD  3        ◆ ◆    ▼    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    ) == situation.draw_pitch(alt_text=False)
    assert (
        "+─────────────+\n"
        "| DET 0               ◆           12           |\n"
        "| SD   3            ◆   ◆       ▼            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25         |\n"
        "+─────────────+"
    ) == situation.draw_pitch(alt_text=True)
    situation = copy.deepcopy(meadows_situation)
