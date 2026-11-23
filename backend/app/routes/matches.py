from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Delivery, Match, Team, Tournament
from app.schemas import InningsSummary, MatchDetail, MatchOut

router = APIRouter(tags=["matches"])


def _names(db, model):
    return {r.id: r.name for r in db.scalars(select(model))}


def _to_out(m, teams, tournaments):
    return {
        "id": m.id, "source_id": m.source_id,
        "tournament": tournaments.get(m.tournament_id),
        "team1": teams[m.team1_id], "team2": teams[m.team2_id],
        "venue": m.venue, "match_date": m.match_date, "match_type": m.match_type,
        "winner": teams.get(m.winner_id),
    }


@router.get("/matches", response_model=list[MatchOut])
def list_matches(team: str | None = None, tournament: str | None = None,
                 limit: int = Query(50, le=200), offset: int = 0, db: Session = Depends(get_db)):
    stmt = select(Match).order_by(Match.match_date.desc(), Match.id.desc())
    if team:
        ids = db.scalars(select(Team.id).where(Team.name.ilike(f"%{team}%"))).all()
        stmt = stmt.where(or_(Match.team1_id.in_(ids), Match.team2_id.in_(ids)))
    if tournament:
        tids = db.scalars(select(Tournament.id).where(Tournament.name.ilike(f"%{tournament}%"))).all()
        stmt = stmt.where(Match.tournament_id.in_(tids))
    matches = db.scalars(stmt.limit(limit).offset(offset)).all()
    teams, tournaments = _names(db, Team), _names(db, Tournament)
    return [_to_out(m, teams, tournaments) for m in matches]


@router.get("/matches/{match_id}", response_model=MatchDetail)
def get_match(match_id: int, db: Session = Depends(get_db)):
    m = db.get(Match, match_id)
    if not m:
        raise HTTPException(404, "match not found")
    teams, tournaments = _names(db, Team), _names(db, Tournament)

    legal = case((Delivery.extra_type.in_(("wides", "noballs")), 0), else_=1)
    wicket = case((Delivery.is_wicket.is_(True), 1), else_=0)
    rows = db.execute(
        select(Delivery.innings, Delivery.batting_team_id,
               func.sum(Delivery.runs_total), func.sum(wicket), func.sum(legal))
        .where(Delivery.match_id == match_id)
        .group_by(Delivery.innings, Delivery.batting_team_id)
        .order_by(Delivery.innings)
    ).all()
    innings = [InningsSummary(innings=r[0], batting_team=teams.get(r[1]),
                              runs=int(r[2] or 0), wickets=int(r[3] or 0), legal_balls=int(r[4] or 0))
               for r in rows]
    total = db.scalar(select(func.count()).select_from(Delivery).where(Delivery.match_id == match_id))
    return MatchDetail(**_to_out(m, teams, tournaments), deliveries_count=total or 0, innings=innings)
