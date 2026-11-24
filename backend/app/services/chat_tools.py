"""Tools the AI assistant can call. Every number it quotes comes from these, not from the model."""
from sqlalchemy import select
from app.models import Delivery, Player
from app.routes import rankings as R
from app.routes.stats import _fetch
from app.services import cache
from app.services.analysis import matchup_stats
from app.services.stats import batting_stats, bowling_stats, group_by_phase

PHASES = ["powerplay", "middle", "death"]
_phase = {"type": "string", "enum": PHASES, "description": "Optional match phase"}
_season = {"type": "integer", "description": "Optional season year, e.g. 2023"}

TOOLS = [
    {"name": "find_player", "description": "Search players by name (Cricsheet style, e.g. 'V Kohli', 'JJ Bumrah'). Returns the ids the other tools need.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "get_bowler_stats", "description": "Bowling stats for one player (economy, wickets, strike rate, dot-ball %, boundary %), overall and by phase.",
     "input_schema": {"type": "object", "properties": {"player_id": {"type": "integer"}, "phase": _phase, "season": _season}, "required": ["player_id"]}},
    {"name": "get_batter_stats", "description": "Batting stats for one player (runs, average, strike rate, dot-ball %, boundary %, dismissals), overall and by phase.",
     "input_schema": {"type": "object", "properties": {"player_id": {"type": "integer"}, "phase": _phase, "season": _season}, "required": ["player_id"]}},
    {"name": "get_matchup", "description": "Head-to-head record of one batter against one bowler.",
     "input_schema": {"type": "object", "properties": {"bowler_id": {"type": "integer"}, "batter_id": {"type": "integer"}}, "required": ["bowler_id", "batter_id"]}},
    {"name": "top_players", "description": "Leaderboard by efficiency score (0-100, relative to other qualified players).",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["bowlers", "batters"]}, "phase": _phase, "season": _season,
                                                      "min_balls": {"type": "integer", "description": "Minimum balls, default 120"},
                                                      "limit": {"type": "integer", "description": "How many to return, default 10"}},
                      "required": ["kind"]}},
]


def _name(db, pid):
    p = db.get(Player, pid)
    return p.name if p else None


def run_tool(db, name, args):
    try:
        phase, season = args.get("phase"), args.get("season")
        if phase and phase not in PHASES:
            return {"error": f"phase must be one of {PHASES}"}
        if name == "find_player":
            rows = db.scalars(select(Player).where(Player.name.ilike(f"%{args['name']}%")).limit(8)).all()
            return {"players": [{"id": p.id, "name": p.name} for p in rows]}
        if name in ("get_bowler_stats", "get_batter_stats"):
            pid = args["player_id"]
            who = _name(db, pid)
            if not who:
                return {"error": "player not found"}
            if name == "get_bowler_stats":
                rows = _fetch(db, "bowler", pid, phase, None, season)
                return {"player": who, "overall": bowling_stats(rows),
                        "by_phase": {k: bowling_stats(g) for k, g in group_by_phase(rows).items()}}
            rows = _fetch(db, "batter", pid, phase, None, season)
            return {"player": who, "overall": batting_stats(rows, pid),
                    "by_phase": {k: batting_stats(g, pid, phase_view=True) for k, g in group_by_phase(rows).items()}}
        if name == "get_matchup":
            b, t = args["bowler_id"], args["batter_id"]
            stmt = select(Delivery.runs_batter, Delivery.extra_type, Delivery.is_wicket, Delivery.wicket_kind).where(
                Delivery.bowler_id == b, Delivery.batter_id == t)
            rows = [dict(r._mapping) for r in db.execute(stmt)]
            return {"bowler": _name(db, b), "batter": _name(db, t), "batter_line_vs_bowler": matchup_stats(rows)}
        if name == "top_players":
            kind, min_balls = args["kind"], int(args.get("min_balls") or 120)
            fn = R._bowlers if kind == "bowlers" else R._batters
            ranked = cache.get_or_compute((kind, min_balls, phase, None, season),
                                          lambda: fn(db, min_balls, phase, None, season))
            return {"kind": kind, "players": [{"rank": r["rank"], "name": r["name"], "player_id": r["player_id"],
                                               "score": r["score"], "stats": r["stats"]}
                                              for r in ranked[:int(args.get("limit") or 10)]]}
        return {"error": f"unknown tool {name}"}
    except Exception as e:  # noqa: BLE001  (let the model see the problem and recover)
        return {"error": str(e)}
