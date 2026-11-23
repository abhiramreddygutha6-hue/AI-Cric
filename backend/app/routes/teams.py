from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Team
from app.schemas import TeamOut

router = APIRouter(tags=["teams"])


@router.get("/teams", response_model=list[TeamOut])
def list_teams(search: str | None = None, limit: int = Query(100, le=500), db: Session = Depends(get_db)):
    stmt = select(Team).order_by(Team.name)
    if search:
        stmt = stmt.where(Team.name.ilike(f"%{search}%"))
    return db.scalars(stmt.limit(limit)).all()
