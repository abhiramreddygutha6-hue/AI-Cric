import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.stats import batting_stats, bowling_stats, group_by_phase


def row(**kw):
    d = dict(match_id=1, innings=1, over_no=0, runs_batter=0, runs_extras=0, runs_total=0,
             extra_type=None, is_wicket=False, wicket_kind=None, phase="powerplay",
             batter_id=10, bowler_id=1, player_out_id=None)
    d.update(kw)
    d["runs_total"] = d["runs_batter"] + d["runs_extras"]
    return d


def test_bowling_stats():
    rows = [
        row(),                                                    # dot
        row(runs_batter=1),
        row(runs_batter=4),                                       # boundary
        row(runs_extras=1, extra_type="wides"),                   # wide: 1 run, not legal
        row(is_wicket=True, wicket_kind="bowled", player_out_id=10),   # wicket + dot
        row(runs_extras=1, extra_type="legbyes"),                 # leg bye: not charged, dot
        row(runs_batter=6),                                       # boundary
        row(runs_batter=2, runs_extras=1, extra_type="noballs"),  # no-ball: 3 runs, not legal
        row(runs_batter=1, is_wicket=True, wicket_kind="run out", player_out_id=10),  # not bowler's wicket
    ]
    s = bowling_stats(rows)
    assert s["balls"] == 7 and s["overs"] == "1.1" and s["runs"] == 16 and s["wickets"] == 1
    assert s["economy"] == 13.71 and s["average"] == 16.0 and s["strike_rate"] == 7.0
    assert s["dots"] == 3 and s["dot_ball_pct"] == 42.86
    assert s["boundaries_conceded"] == 2 and s["boundary_pct"] == 28.57
    assert s["wides"] == 1 and s["no_balls"] == 1


def test_bowling_empty():
    s = bowling_stats([])
    assert s["balls"] == 0 and s["economy"] is None and s["average"] is None


def test_batting_stats():
    rows = [
        row(runs_batter=4), row(), row(runs_batter=6),
        row(runs_extras=1, extra_type="wides"),                   # wide: not a ball faced
        row(runs_batter=1),
        row(is_wicket=True, wicket_kind="bowled", player_out_id=10),
    ]
    rows += [row(match_id=2, runs_batter=6, phase="death") for _ in range(9)]   # 54 not out
    rows.append(row(match_id=3, batter_id=99, is_wicket=True, wicket_kind="run out", player_out_id=10))
    rows.append(row(match_id=4, batter_id=99, is_wicket=True, wicket_kind="retired hurt", player_out_id=10))
    s = batting_stats(rows, 10)
    assert s["innings"] == 3 and s["dismissals"] == 2 and s["not_outs"] == 1
    assert s["runs"] == 65 and s["balls"] == 14
    assert s["average"] == 32.5 and s["strike_rate"] == 464.29
    assert s["fours"] == 1 and s["sixes"] == 10
    assert s["boundary_pct"] == 78.57 and s["dot_ball_pct"] == 14.29
    assert s["highest_score"] == 54 and s["fifties"] == 1 and s["hundreds"] == 0
    assert s["dismissals_by_kind"] == {"bowled": 1, "run out": 1}


def test_phase_grouping_and_phase_view():
    rows = [row(phase="powerplay", runs_batter=1), row(phase="death", runs_batter=6), row(phase=None)]
    groups = group_by_phase(rows)
    assert set(groups) == {"powerplay", "death", "other"}
    assert batting_stats(groups["death"], 10, phase_view=True)["not_outs"] is None
    assert bowling_stats(groups["death"])["runs"] == 6
