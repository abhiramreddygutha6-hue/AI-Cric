from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, or_, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Delivery, Match, Player, Tournament
from app.schemas_stats import BatterReport, BowlerReport
from app.services.stats import batting_stats, bowling_stats, group_by_phase

router = APIRouter(tags=["stats"])
Phase = Literal["powerplay", "middle", "death"]

COLUMNS = (Delivery.match_id, Delivery.innings, Delivery.over_no, Delivery.runs_batter,
           Delivery.runs_extras, Delivery.runs_total, Delivery.extra_type, Delivery.is_wicket,
           Delivery.wicket_kind, Delivery.phase, Delivery.batter_id, Delivery.bowler_id,
           Delivery.player_out_id)


def _fetch(db, who, player_id, phase, tournament, season):
    stmt = select(*COLUMNS).join(Match, Match.id == Delivery.match_id)
    if who == "bowler":
        stmt = stmt.where(Delivery.bowler_id == player_id)
    else:  # batter: balls faced, plus dismissals (including run outs at the other end)
        stmt = stmt.where(or_(Delivery.batter_id == player_id, Delivery.player_out_id == player_id))
    if phase:
        stmt = stmt.where(Delivery.phase == phase)
    if tournament:
        stmt = stmt.join(Tournament, Tournament.id == Match.tournament_id) \
                   .where(Tournament.name.ilike(f"%{tournament}%"))
    if season:
        stmt = stmt.where(extract("year", Match.match_date) == season)
    return [dict(r._mapping) for r in db.execute(stmt)]


def _filters(phase, tournament, season):
    f = {"phase": phase, "tournament": tournament, "season": season}
    return {k: v for k, v in f.items() if v is not None}


def _player(db, player_id):
    p = db.get(Player, player_id)
    if not p:
        raise HTTPException(404, "player not found")
    return p


@router.get("/stats/bowlers/{player_id}", response_model=BowlerReport)
def bowler_report(player_id: int, phase: Phase | None = None, tournament: str | None = None,
                  season: int | None = None, db: Session = Depends(get_db)):
    player = _player(db, player_id)
    rows = _fetch(db, "bowler", player_id, phase, tournament, season)
    return {"player": player, "filters": _filters(phase, tournament, season),
            "overall": bowling_stats(rows),
            "by_phase": {k: bowling_stats(g) for k, g in group_by_phase(rows).items()}}


@router.get("/stats/batters/{player_id}", response_model=BatterReport)
def batter_report(player_id: int, phase: Phase | None = None, tournament: str | None = None,
                  season: int | None = None, db: Session = Depends(get_db)):
    player = _player(db, player_id)
    rows = _fetch(db, "batter", player_id, phase, tournament, season)
    return {"player": player, "filters": _filters(phase, tournament, season),
            "overall": batting_stats(rows, player_id),
            "by_phase": {k: batting_stats(g, player_id, phase_view=True)
                         for k, g in group_by_phase(rows).items()}}
