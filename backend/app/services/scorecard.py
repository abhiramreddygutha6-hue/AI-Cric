"""Turn an uploaded scorecard CSV (one match) into the same dict shape as cricsheet.parse_match."""
import re
from app.services.cricsheet import normalize_match_type, phase_for

REQUIRED = ["innings", "batting_team", "over", "ball", "bowler", "batter", "runs_batter"]
VALID_EXTRAS = {"wides", "noballs", "byes", "legbyes", "penalty"}


def _int(row, key, rownum, default=None):
    v = (row.get(key) or "").strip()
    if v == "":
        if default is None:
            raise ValueError(f"row {rownum}: '{key}' is required")
        return default
    try:
        return int(v)
    except ValueError:
        raise ValueError(f"row {rownum}: '{key}' must be a whole number, got '{v}'")


def _text(row, key):
    v = (row.get(key) or "").strip()
    return v or None


def csv_rows_to_match(rows, meta):
    """rows: list of dicts from csv.DictReader. meta: team1, team2, match_date, venue,
    tournament, match_type, winner. Over numbers in the CSV start at 1."""
    if not rows:
        raise ValueError("the CSV has no data rows")
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        raise ValueError(f"missing column(s): {', '.join(missing)}")

    team1, team2 = meta["team1"].strip(), meta["team2"].strip()
    if team1 == team2:
        raise ValueError("team1 and team2 must be different")
    winner = (meta.get("winner") or "").strip() or None
    if winner and winner not in (team1, team2):
        raise ValueError("winner must be team1 or team2")

    match_type = normalize_match_type(meta.get("match_type") or "T20")
    deliveries = []
    for i, row in enumerate(rows, start=2):  # row 1 is the header
        batting_team = (row.get("batting_team") or "").strip()
        if batting_team not in (team1, team2):
            raise ValueError(f"row {i}: batting_team '{batting_team}' is not {team1} or {team2}")
        over = _int(row, "over", i)
        if over < 1:
            raise ValueError(f"row {i}: 'over' starts at 1")
        extra_type = _text(row, "extra_type")
        if extra_type and extra_type not in VALID_EXTRAS:
            raise ValueError(f"row {i}: extra_type must be one of {sorted(VALID_EXTRAS)}")
        runs_batter = _int(row, "runs_batter", i)
        runs_extras = _int(row, "runs_extras", i, default=0)
        wicket_kind = _text(row, "wicket_kind")
        bowler, batter = _text(row, "bowler"), _text(row, "batter")
        if not bowler or not batter:
            raise ValueError(f"row {i}: bowler and batter are required")
        deliveries.append({
            "innings": _int(row, "innings", i),
            "batting_team": batting_team,
            "over_no": over - 1,
            "ball_no": _int(row, "ball", i),
            "bowler": bowler,
            "batter": batter,
            "non_striker": _text(row, "non_striker"),
            "runs_batter": runs_batter,
            "runs_extras": runs_extras,
            "runs_total": runs_batter + runs_extras,
            "extra_type": extra_type,
            "is_wicket": wicket_kind is not None,
            "wicket_kind": wicket_kind,
            "player_out": _text(row, "player_out") or (batter if wicket_kind else None),
            "phase": phase_for(match_type, over - 1),
        })

    slug = re.sub(r"[^a-z0-9]+", "-", f"{meta['match_date']}-{team1}-{team2}".lower()).strip("-")
    return {
        "source_id": f"csv-{slug}",
        "match_type": match_type,
        "match_date": meta["match_date"],
        "venue": (meta.get("venue") or "").strip() or None,
        "tournament": (meta.get("tournament") or "").strip() or None,
        "team1": team1,
        "team2": team2,
        "winner": winner,
        "registry": {},
        "deliveries": deliveries,
    }
