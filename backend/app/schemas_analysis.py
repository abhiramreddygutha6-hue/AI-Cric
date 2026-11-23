from typing import Optional
from pydantic import BaseModel
from app.schemas import PlayerOut


class BatterLine(BaseModel):
    balls: int
    runs: int
    dismissals: int
    average: Optional[float] = None
    strike_rate: Optional[float] = None
    dot_ball_pct: Optional[float] = None
    boundary_pct: Optional[float] = None
    fours: int
    sixes: int


class MatchupRow(BatterLine):
    opponent_id: int
    opponent_name: str


class MatchupReport(BaseModel):
    bowler: PlayerOut
    batter: PlayerOut
    overall: BatterLine
    by_phase: dict[str, BatterLine]


class BowlerLine(BaseModel):
    balls: int
    overs: str
    runs: int
    wickets: int
    economy: Optional[float] = None
    average: Optional[float] = None
    strike_rate: Optional[float] = None
    dot_ball_pct: Optional[float] = None
    boundary_pct: Optional[float] = None


class RankedBowler(BaseModel):
    rank: int
    player_id: int
    name: str
    score: float
    components: dict[str, float]
    stats: BowlerLine


class RankedBatter(BaseModel):
    rank: int
    player_id: int
    name: str
    score: float
    components: dict[str, float]
    stats: BatterLine
