"""Bowling and batting statistics.

compute functions take plain row dicts (no database), so they are easy to test.
Conventions (standard cricket scoring):
- Bowler is charged: runs off the bat + wides + no-balls. Byes and leg byes are NOT charged.
- Legal ball = not a wide and not a no-ball. Overs/economy use legal balls only.
- Bowler wickets exclude run outs, retirements and similar.
- Batter balls faced exclude wides but include no-balls.
- Batter average = runs / dismissals ("retired hurt" is not a dismissal).
"""
from collections import Counter

CHARGED_EXTRAS = {"wides", "noballs"}
BOWLER_WICKET_KINDS = {"bowled", "caught", "lbw", "stumped", "caught and bowled", "hit wicket"}
NOT_A_DISMISSAL = {"retired hurt", "retired not out"}


def _div(a, b, scale=1):
    return round(a * scale / b, 2) if b else None


def _overs(legal_balls):
    return f"{legal_balls // 6}.{legal_balls % 6}"


def bowling_stats(rows):
    legal = runs = wickets = dots = boundaries = wides = noballs = 0
    for r in rows:
        et = r["extra_type"]
        cost = r["runs_batter"] + (r["runs_extras"] if et in CHARGED_EXTRAS else 0)
        runs += cost
        if et == "wides":
            wides += 1
        elif et == "noballs":
            noballs += 1
        else:
            legal += 1
            if cost == 0:
                dots += 1
            if r["runs_batter"] in (4, 6):
                boundaries += 1
        if r["is_wicket"] and r["wicket_kind"] in BOWLER_WICKET_KINDS:
            wickets += 1
    return {
        "balls": legal, "overs": _overs(legal), "runs": runs, "wickets": wickets,
        "economy": _div(runs, legal, 6), "average": _div(runs, wickets),
        "strike_rate": _div(legal, wickets), "dot_ball_pct": _div(dots, legal, 100),
        "boundary_pct": _div(boundaries, legal, 100),
        "dots": dots, "boundaries_conceded": boundaries, "wides": wides, "no_balls": noballs,
    }


def batting_stats(rows, player_id, phase_view=False):
    """rows must include every delivery where the player faced a ball OR was dismissed
    (a run out at the non-striker's end has the player only in player_out_id)."""
    balls = runs = fours = sixes = dots = dismissals = 0
    innings_keys, per_innings = set(), {}
    kinds, phases = Counter(), Counter()
    for r in rows:
        key = (r["match_id"], r["innings"])
        if r["batter_id"] == player_id:
            innings_keys.add(key)
            rb = r["runs_batter"]
            runs += rb
            per_innings[key] = per_innings.get(key, 0) + rb
            if r["extra_type"] != "wides":
                balls += 1
                if rb == 0:
                    dots += 1
                elif rb == 4:
                    fours += 1
                elif rb == 6:
                    sixes += 1
        if (r["player_out_id"] == player_id and r["is_wicket"]
                and r["wicket_kind"] not in NOT_A_DISMISSAL):
            innings_keys.add(key)
            dismissals += 1
            kinds[r["wicket_kind"]] += 1
            phases[r["phase"] or "other"] += 1
    innings = len(innings_keys)
    scores = list(per_innings.values())
    return {
        "innings": innings, "balls": balls, "runs": runs, "dismissals": dismissals,
        "not_outs": None if phase_view else max(innings - dismissals, 0),
        "average": _div(runs, dismissals), "strike_rate": _div(runs, balls, 100),
        "dot_ball_pct": _div(dots, balls, 100), "boundary_pct": _div(fours + sixes, balls, 100),
        "fours": fours, "sixes": sixes,
        "highest_score": max(scores) if scores else None,
        "fifties": sum(1 for s in scores if 50 <= s < 100),
        "hundreds": sum(1 for s in scores if s >= 100),
        "dismissals_by_kind": dict(kinds), "dismissals_by_phase": dict(phases),
    }


def group_by_phase(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["phase"] or "other", []).append(r)
    return groups
