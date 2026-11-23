"""Save parsed matches (from Cricsheet or CSV) into the database."""
import json
from pathlib import Path
from sqlalchemy import insert, select
from app.models import Delivery, Match, Player, Team, Tournament
from app.services.cricsheet import parse_match


class Cache:
    """Remembers ids so we don't query the DB for every ball."""

    def __init__(self):
        self.teams, self.tournaments = {}, {}
        self.players_by_cid, self.players_by_name = {}, {}
        self.source_ids = set()

    @classmethod
    def load(cls, db):
        c = cls()
        for t in db.scalars(select(Team)):
            c.teams[t.name] = t.id
        for t in db.scalars(select(Tournament)):
            c.tournaments[t.name] = t.id
        for p in db.scalars(select(Player)):
            if p.cricsheet_id:
                c.players_by_cid[p.cricsheet_id] = p.id
            c.players_by_name[p.name] = p.id
        c.source_ids = set(db.scalars(select(Match.source_id)).all())
        return c

    def team_id(self, db, name):
        if name not in self.teams:
            t = Team(name=name)
            db.add(t)
            db.flush()
            self.teams[name] = t.id
        return self.teams[name]

    def tournament_id(self, db, name):
        if not name:
            return None
        if name not in self.tournaments:
            t = Tournament(name=name)
            db.add(t)
            db.flush()
            self.tournaments[name] = t.id
        return self.tournaments[name]

    def player_id(self, db, name, cricsheet_id=None):
        if cricsheet_id and cricsheet_id in self.players_by_cid:
            return self.players_by_cid[cricsheet_id]
        if not cricsheet_id and name in self.players_by_name:
            return self.players_by_name[name]
        p = Player(name=name, cricsheet_id=cricsheet_id)
        db.add(p)
        db.flush()
        if cricsheet_id:
            self.players_by_cid[cricsheet_id] = p.id
        self.players_by_name[name] = p.id
        return p.id


def save_parsed_match(db, pm, cache):
    """Returns the new match id, or None if this source_id was already imported.
    The caller commits."""
    if pm["source_id"] in cache.source_ids:
        return None

    team1 = cache.team_id(db, pm["team1"])
    team2 = cache.team_id(db, pm["team2"])
    match = Match(
        source_id=pm["source_id"],
        tournament_id=cache.tournament_id(db, pm["tournament"]),
        team1_id=team1,
        team2_id=team2,
        venue=pm["venue"],
        match_date=pm["match_date"],
        match_type=pm["match_type"],
        winner_id=cache.team_id(db, pm["winner"]) if pm["winner"] else None,
    )
    db.add(match)
    db.flush()

    reg = pm["registry"]

    def pid(name):
        return cache.player_id(db, name, reg.get(name)) if name else None

    rows = []
    for d in pm["deliveries"]:
        rows.append({
            "match_id": match.id,
            "innings": d["innings"],
            "batting_team_id": cache.team_id(db, d["batting_team"]),
            "over_no": d["over_no"],
            "ball_no": d["ball_no"],
            "bowler_id": pid(d["bowler"]),
            "batter_id": pid(d["batter"]),
            "non_striker_id": pid(d["non_striker"]),
            "runs_batter": d["runs_batter"],
            "runs_extras": d["runs_extras"],
            "runs_total": d["runs_total"],
            "extra_type": d["extra_type"],
            "is_wicket": d["is_wicket"],
            "wicket_kind": d["wicket_kind"],
            "player_out_id": pid(d["player_out"]),
            "phase": d["phase"],
        })
    if rows:
        db.execute(insert(Delivery), rows)
    cache.source_ids.add(pm["source_id"])
    return match.id


def import_folder(db, folder, limit=None, log=print):
    """Import every Cricsheet *.json in a folder. Safe to re-run: already-imported
    matches are skipped. A bad file is reported and skipped, not fatal."""
    files = sorted(Path(folder).glob("*.json"))
    cache = Cache.load(db)
    stats = {"imported": 0, "skipped": 0, "failed": 0}
    for f in files:
        if limit and stats["imported"] >= limit:
            break
        if f.stem in cache.source_ids:
            stats["skipped"] += 1
            continue
        try:
            pm = parse_match(json.loads(f.read_text(encoding="utf-8")), f.stem)
            save_parsed_match(db, pm, cache)
            db.commit()
            stats["imported"] += 1
            if stats["imported"] % 50 == 0:
                log(f"  imported {stats['imported']} matches...")
        except Exception as e:  # noqa: BLE001
            db.rollback()
            cache = Cache.load(db)  # drop ids from the rolled-back match
            stats["failed"] += 1
            log(f"  FAILED {f.name}: {e}")
    return stats
