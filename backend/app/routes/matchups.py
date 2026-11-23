from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Delivery, Player
from app.schemas_analysis import MatchupReport, MatchupRow
from app.services import sql_exprs as X
from app.services.analysis import batter_line, matchup_stats
from app.services.stats import group_by_phase

router = APIRouter(tags=["matchups"])
Phase = Literal["powerplay", "middle", "death"]


def _player(db, player_id):
    p = db.get(Player, player_id)
    if not p:
        raise HTTPException(404, f"player {player_id} not found")
    return p


@router.get("/matchups", response_model=MatchupReport)
def head_to_head(bowler_id: int, batter_id: int, db: Session = Depends(get_db)):
    bowler, batter = _player(db, bowler_id), _player(db, batter_id)
    stmt = select(Delivery.runs_batter, Delivery.extra_type, Delivery.is_wicket,
                  Delivery.wicket_kind, Delivery.phase).where(
        Delivery.bowler_id == bowler_id, Delivery.batter_id == batter_id)
    rows = [dict(r._mapping) for r in db.execute(stmt)]
    return {"bowler": bowler, "batter": batter, "overall": matchup_stats(rows),
            "by_phase": {k: matchup_stats(g) for k, g in group_by_phase(rows).items()}}


def _grouped(db, focus, player_id, min_balls, limit, sort, phase, tournament, season):
    _player(db, player_id)
    group_col = Delivery.batter_id if focus == "bowler" else Delivery.bowler_id
    focus_col = Delivery.bowler_id if focus == "bowler" else Delivery.batter_id
    stmt = (select(group_col, func.sum(X.faced_n), func.sum(Delivery.runs_batter),
                   func.sum(X.bowler_wicket), func.sum(X.faced_dot),
                   func.sum(X.faced_four), func.sum(X.faced_six))
            .where(focus_col == player_id).group_by(group_col)
            .having(func.sum(X.faced_n) >= min_balls))
    stmt = X.scope(stmt, phase, tournament, season)
    names = dict(db.execute(select(Player.id, Player.name)).all())
    out = []
    for opp, balls, runs, wkts, dots, fours, sixes in db.execute(stmt):
        line = batter_line(int(balls or 0), int(runs or 0), int(wkts or 0),
                           int(dots or 0), int(fours or 0), int(sixes or 0))
        out.append({"opponent_id": opp, "opponent_name": names.get(opp, "?"), **line})
    out.sort(key=lambda r: r[sort], reverse=True)
    return out[:limit]


@router.get("/matchups/bowler/{player_id}", response_model=list[MatchupRow])
def bowler_matchups(player_id: int, min_balls: int = Query(6, ge=1), limit: int = Query(20, ge=1, le=200),
                    sort: Literal["balls", "dismissals", "runs"] = "balls", phase: Phase | None = None,
                    tournament: str | None = None, season: int | None = None,
                    db: Session = Depends(get_db)):
    """How each batter has fared against this bowler."""
    return _grouped(db, "bowler", player_id, min_balls, limit, sort, phase, tournament, season)


@router.get("/matchups/batter/{player_id}", response_model=list[MatchupRow])
def batter_matchups(player_id: int, min_balls: int = Query(6, ge=1), limit: int = Query(20, ge=1, le=200),
                    sort: Literal["balls", "dismissals", "runs"] = "balls", phase: Phase | None = None,
                    tournament: str | None = None, season: int | None = None,
                    db: Session = Depends(get_db)):
    """How this batter has fared against each bowler."""
    return _grouped(db, "batter", player_id, min_balls, limit, sort, phase, tournament, season)
