import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.analysis import (batter_line, batter_metrics, bowler_line, bowler_metrics,
                                   matchup_stats, percentile_ranks, score_players,
                                   BATTER_LOWER_BETTER, BATTER_WEIGHTS,
                                   BOWLER_LOWER_BETTER, BOWLER_WEIGHTS)
from app.services.stats import batting_stats, bowling_stats


def row(**kw):
    d = dict(match_id=1, innings=1, over_no=0, runs_batter=0, runs_extras=0, runs_total=0,
             extra_type=None, is_wicket=False, wicket_kind=None, phase="powerplay",
             batter_id=10, bowler_id=1, player_out_id=None)
    d.update(kw)
    d["runs_total"] = d["runs_batter"] + d["runs_extras"]
    return d


H2H_ROWS = [
    row(),                                                          # dot
    row(runs_batter=4),
    row(runs_batter=6),
    row(runs_batter=1),
    row(runs_extras=1, extra_type="wides"),                         # wide: not faced
    row(is_wicket=True, wicket_kind="bowled", player_out_id=10),    # dot + dismissal
    row(runs_batter=4, runs_extras=1, extra_type="noballs"),        # no-ball: faced
]


def test_percentile_ranks():
    assert [round(x, 2) for x in percentile_ranks([1, 2, 3])] == [16.67, 50.0, 83.33]
    assert [round(x, 2) for x in percentile_ranks([1, 2, 3], higher_is_better=False)] == [83.33, 50.0, 16.67]
    assert percentile_ranks([5, 5]) == [50.0, 50.0]                 # ties share the middle


def test_bowler_scoring_order():
    m = {
        "A": {"economy": 6, "strike_rate": 12, "dot_ball_pct": 50, "boundary_pct": 10},
        "B": {"economy": 8, "strike_rate": 18, "dot_ball_pct": 40, "boundary_pct": 15},
        "C": {"economy": 10, "strike_rate": float("inf"), "dot_ball_pct": 30, "boundary_pct": 20},
    }
    s = score_players(m, BOWLER_WEIGHTS, BOWLER_LOWER_BETTER)
    assert s["A"]["score"] == 83.33 and s["B"]["score"] == 50.0 and s["C"]["score"] == 16.67
    assert s["A"]["components"]["economy"] == 83.33


def test_batter_scoring_order():
    m = {
        "A": {"strike_rate": 150, "average": 40, "boundary_pct": 20, "dot_ball_pct": 30},
        "B": {"strike_rate": 120, "average": 30, "boundary_pct": 15, "dot_ball_pct": 40},
        "C": {"strike_rate": 90, "average": 20, "boundary_pct": 10, "dot_ball_pct": 50},
    }
    s = score_players(m, BATTER_WEIGHTS, BATTER_LOWER_BETTER)
    assert (s["A"]["score"], s["B"]["score"], s["C"]["score"]) == (83.33, 50.0, 16.67)


def test_score_empty_and_missing_values():
    assert score_players({}, BOWLER_WEIGHTS, BOWLER_LOWER_BETTER) == {}
    no_wickets = bowler_line(120, 150, 0, 40, 10)           # strike rate None
    assert bowler_metrics(no_wickets)["strike_rate"] == float("inf")
    never_out = batter_line(100, 80, 0, 30, 5, 3)           # average None
    assert batter_metrics(never_out)["average"] == 80.0


def test_totals_match_row_stats():
    bowl_rows = [
        row(), row(runs_batter=1), row(runs_batter=4), row(runs_extras=1, extra_type="wides"),
        row(is_wicket=True, wicket_kind="bowled", player_out_id=10),
        row(runs_extras=1, extra_type="legbyes"), row(runs_batter=6),
        row(runs_batter=2, runs_extras=1, extra_type="noballs"),
        row(runs_batter=1, is_wicket=True, wicket_kind="run out", player_out_id=10),
    ]
    full = bowling_stats(bowl_rows)
    line = bowler_line(balls=7, runs=16, wickets=1, dots=3, boundaries=2)
    for k in line:
        assert line[k] == full[k], k

    full = batting_stats(H2H_ROWS, 10)
    line = batter_line(balls=6, runs=15, dismissals=1, dots=2, fours=2, sixes=1)
    for k in line:
        assert line[k] == full[k], k


def test_matchup_stats():
    s = matchup_stats(H2H_ROWS)
    assert s["balls"] == 6 and s["runs"] == 15 and s["dismissals"] == 1
    assert s["strike_rate"] == 250.0 and s["average"] == 15.0
    assert s["dot_ball_pct"] == 33.33 and s["boundary_pct"] == 50.0
    assert s["fours"] == 2 and s["sixes"] == 1


def test_matchup_run_out_not_credited_to_bowler():
    s = matchup_stats([row(runs_batter=1, is_wicket=True, wicket_kind="run out", player_out_id=10)])
    assert s["dismissals"] == 0 and s["balls"] == 1
