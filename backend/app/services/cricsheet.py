"""Parse Cricsheet ball-by-ball JSON into plain dicts. No database code here."""
from datetime import date

MATCH_TYPE_MAP = {"T20": "T20", "IT20": "T20", "ODI": "ODI", "ODM": "ODI", "Test": "Test", "MDM": "Test"}
EXTRA_PRIORITY = ("wides", "noballs", "byes", "legbyes", "penalty")


def normalize_match_type(raw):
    return MATCH_TYPE_MAP.get(raw, raw or "Other")


def phase_for(match_type, over_no):
    """over_no is 0-based. Returns powerplay / middle / death, or None (e.g. Tests)."""
    if match_type == "T20":
        return "powerplay" if over_no < 6 else "middle" if over_no < 16 else "death"
    if match_type == "ODI":
        return "powerplay" if over_no < 10 else "middle" if over_no < 40 else "death"
    return None


def parse_match(data, source_id):
    info = data["info"]
    teams = info.get("teams") or []
    if len(teams) != 2:
        raise ValueError("expected exactly 2 teams")

    match_type = normalize_match_type(info.get("match_type"))
    event = info.get("event")
    tournament = event.get("name") if isinstance(event, dict) else event
    dates = info.get("dates") or []
    registry = (info.get("registry") or {}).get("people", {})

    deliveries = []
    innings_no = 0
    for inn in data.get("innings", []):
        if inn.get("super_over"):
            continue  # keep super overs out of normal stats
        innings_no += 1
        for ov in inn.get("overs", []):
            over_no = ov["over"]
            for ball_no, d in enumerate(ov["deliveries"], start=1):
                extras = d.get("extras", {})
                extra_type = next((k for k in EXTRA_PRIORITY if k in extras), None)
                wickets = d.get("wickets") or []
                w = wickets[0] if wickets else None
                deliveries.append({
                    "innings": innings_no,
                    "batting_team": inn["team"],
                    "over_no": over_no,
                    "ball_no": ball_no,
                    "bowler": d["bowler"],
                    "batter": d["batter"],
                    "non_striker": d.get("non_striker"),
                    "runs_batter": d["runs"]["batter"],
                    "runs_extras": d["runs"].get("extras", 0),
                    "runs_total": d["runs"]["total"],
                    "extra_type": extra_type,
                    "is_wicket": w is not None,
                    "wicket_kind": w["kind"] if w else None,
                    "player_out": w["player_out"] if w else None,
                    "phase": phase_for(match_type, over_no),
                })

    return {
        "source_id": source_id,
        "match_type": match_type,
        "match_date": date.fromisoformat(str(dates[0])) if dates else None,
        "venue": info.get("venue"),
        "tournament": tournament,
        "team1": teams[0],
        "team2": teams[1],
        "winner": (info.get("outcome") or {}).get("winner"),
        "registry": registry,
        "deliveries": deliveries,
    }
