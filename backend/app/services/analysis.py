"""Efficiency scores, rankings math and matchup lines. No database code here.

Scoring method: each metric is converted to a percentile rank (0-100) within the pool of
qualified players, then combined with fixed weights into one 0-100 score. Percentiles avoid
arbitrary benchmarks and outlier distortion, but a score is relative to the pool it is
computed in (the filters you choose: phase, tournament, season, min balls).
"""
from bisect import bisect_left, bisect_right
from app.services.stats import BOWLER_WICKET_KINDS, _div, _overs

INF = float("inf")

BOWLER_WEIGHTS = {"economy": 35, "strike_rate": 25, "dot_ball_pct": 25, "boundary_pct": 15}
BOWLER_LOWER_BETTER = {"economy", "strike_rate", "boundary_pct"}
BATTER_WEIGHTS = {"strike_rate": 30, "average": 30, "boundary_pct": 20, "dot_ball_pct": 20}
BATTER_LOWER_BETTER = {"dot_ball_pct"}


def percentile_ranks(values, higher_is_better=True):
    n = len(values)
    s = sorted(values)
    out = []
    for v in values:
        lo, hi = bisect_left(s, v), bisect_right(s, v)
        pct = (lo + 0.5 * (hi - lo)) / n * 100
        out.append(pct if higher_is_better else 100 - pct)
    return out


def score_players(metrics_by_id, weights, lower_better):
    """metrics_by_id: {player_id: {metric: number}} -> {player_id: {score, components}}"""
    ids = list(metrics_by_id)
    if not ids:
        return {}
    total_w = sum(weights.values())
    pct = {}
    for m in weights:
        vals = [metrics_by_id[i][m] for i in ids]
        pct[m] = dict(zip(ids, percentile_ranks(vals, higher_is_better=m not in lower_better)))
    out = {}
    for i in ids:
        score = sum(weights[m] * pct[m][i] for m in weights) / total_w
        out[i] = {"score": round(score, 2), "components": {m: round(pct[m][i], 2) for m in weights}}
    return out


def bowler_line(balls, runs, wickets, dots, boundaries):
    return {
        "balls": balls, "overs": _overs(balls), "runs": runs, "wickets": wickets,
        "economy": _div(runs, balls, 6), "average": _div(runs, wickets),
        "strike_rate": _div(balls, wickets), "dot_ball_pct": _div(dots, balls, 100),
        "boundary_pct": _div(boundaries, balls, 100),
    }


def batter_line(balls, runs, dismissals, dots, fours, sixes):
    return {
        "balls": balls, "runs": runs, "dismissals": dismissals,
        "average": _div(runs, dismissals), "strike_rate": _div(runs, balls, 100),
        "dot_ball_pct": _div(dots, balls, 100), "boundary_pct": _div(fours + sixes, balls, 100),
        "fours": fours, "sixes": sixes,
    }


def bowler_metrics(line):
    """A bowler with no wickets gets the worst possible strike rate."""
    sr = line["strike_rate"]
    return {"economy": line["economy"], "strike_rate": INF if sr is None else sr,
            "dot_ball_pct": line["dot_ball_pct"], "boundary_pct": line["boundary_pct"]}


def batter_metrics(line):
    """A batter never dismissed has no average, so use runs / 1."""
    avg = line["average"] if line["average"] is not None else float(line["runs"])
    return {"strike_rate": line["strike_rate"], "average": avg,
            "boundary_pct": line["boundary_pct"], "dot_ball_pct": line["dot_ball_pct"]}


def matchup_stats(rows):
    """Batter's line against one bowler. Balls = balls faced (no wides); dismissals = wickets
    credited to the bowler (run outs and retirements excluded)."""
    balls = runs = dots = fours = sixes = dismissals = 0
    for r in rows:
        rb = r["runs_batter"]
        runs += rb
        if r["extra_type"] != "wides":
            balls += 1
            if rb == 0:
                dots += 1
            elif rb == 4:
                fours += 1
            elif rb == 6:
                sixes += 1
        if r["is_wicket"] and r["wicket_kind"] in BOWLER_WICKET_KINDS:
            dismissals += 1
    return batter_line(balls, runs, dismissals, dots, fours, sixes)
