from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Player
from app.schemas import PlayerOut

router = APIRouter(tags=["players"])


@router.get("/players", response_model=list[PlayerOut])
def list_players(search: str | None = None, limit: int = Query(50, le=200), offset: int = 0,
                 db: Session = Depends(get_db)):
    stmt = select(Player).order_by(Player.name)
    if search:
        stmt = stmt.where(Player.name.ilike(f"%{search}%"))
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@router.get("/players/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(404, "player not found")
    return player
