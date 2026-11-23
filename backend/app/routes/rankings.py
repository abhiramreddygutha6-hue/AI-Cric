from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Delivery, Player
from app.schemas_analysis import RankedBatter, RankedBowler
from app.services import cache
from app.services import sql_exprs as X
from app.services.analysis import (BATTER_LOWER_BETTER, BATTER_WEIGHTS, BOWLER_LOWER_BETTER,
                                   BOWLER_WEIGHTS, batter_line, batter_metrics, bowler_line,
                                   bowler_metrics, score_players)

router = APIRouter(tags=["rankings"])
Phase = Literal["powerplay", "middle", "death"]


def _rank(lines, metrics_fn, weights, lower_better, names):
    scores = score_players({i: metrics_fn(l) for i, l in lines.items()}, weights, lower_better)
    order = sorted(lines, key=lambda i: scores[i]["score"], reverse=True)
    return [{"rank": n, "player_id": i, "name": names.get(i, "?"), "score": scores[i]["score"],
             "components": scores[i]["components"], "stats": lines[i]}
            for n, i in enumerate(order, start=1)]


def _names(db):
    return dict(db.execute(select(Player.id, Player.name)).all())


def _bowlers(db, min_balls, phase, tournament, season):
    stmt = (select(Delivery.bowler_id, func.sum(X.legal_n), func.sum(X.charged_runs),
                   func.sum(X.bowler_wicket), func.sum(X.legal_dot_charged), func.sum(X.legal_boundary))
            .group_by(Delivery.bowler_id).having(func.sum(X.legal_n) >= min_balls))
    stmt = X.scope(stmt, phase, tournament, season)
    lines = {r[0]: bowler_line(*(int(v or 0) for v in r[1:])) for r in db.execute(stmt)}
    return _rank(lines, bowler_metrics, BOWLER_WEIGHTS, BOWLER_LOWER_BETTER, _names(db))


def _batters(db, min_balls, phase, tournament, season):
    stmt = (select(Delivery.batter_id, func.sum(X.faced_n), func.sum(Delivery.runs_batter),
                   func.sum(X.faced_dot), func.sum(X.faced_four), func.sum(X.faced_six))
            .group_by(Delivery.batter_id).having(func.sum(X.faced_n) >= min_balls))
    stmt = X.scope(stmt, phase, tournament, season)
    rows = db.execute(stmt).all()
    dstmt = (select(Delivery.player_out_id, func.sum(X.dismissal))
             .where(Delivery.player_out_id.is_not(None)).group_by(Delivery.player_out_id))
    dism = {r[0]: int(r[1] or 0) for r in db.execute(X.scope(dstmt, phase, tournament, season))}
    lines = {}
    for pid, balls, runs, dots, fours, sixes in rows:
        lines[pid] = batter_line(int(balls or 0), int(runs or 0), dism.get(pid, 0),
                                 int(dots or 0), int(fours or 0), int(sixes or 0))
    return _rank(lines, batter_metrics, BATTER_WEIGHTS, BATTER_LOWER_BETTER, _names(db))


@router.get("/rankings/bowlers", response_model=list[RankedBowler])
def rank_bowlers(min_balls: int = Query(120, ge=1), limit: int = Query(20, ge=1, le=200),
                 phase: Phase | None = None, tournament: str | None = None,
                 season: int | None = None, db: Session = Depends(get_db)):
    key = ("bowlers", min_balls, phase, tournament, season)
    ranked = cache.get_or_compute(key, lambda: _bowlers(db, min_balls, phase, tournament, season))
    return ranked[:limit]


@router.get("/rankings/batters", response_model=list[RankedBatter])
def rank_batters(min_balls: int = Query(120, ge=1), limit: int = Query(20, ge=1, le=200),
                 phase: Phase | None = None, tournament: str | None = None,
                 season: int | None = None, db: Session = Depends(get_db)):
    key = ("batters", min_balls, phase, tournament, season)
    ranked = cache.get_or_compute(key, lambda: _batters(db, min_balls, phase, tournament, season))
    return ranked[:limit]
