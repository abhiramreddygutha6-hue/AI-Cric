from typing import Optional
from pydantic import BaseModel
from app.schemas import PlayerOut


class BowlingStats(BaseModel):
    balls: int
    overs: str
    runs: int
    wickets: int
    economy: Optional[float] = None
    average: Optional[float] = None
    strike_rate: Optional[float] = None
    dot_ball_pct: Optional[float] = None
    boundary_pct: Optional[float] = None
    dots: int
    boundaries_conceded: int
    wides: int
    no_balls: int


class BattingStats(BaseModel):
    innings: int
    balls: int
    runs: int
    dismissals: int
    not_outs: Optional[int] = None
    average: Optional[float] = None
    strike_rate: Optional[float] = None
    dot_ball_pct: Optional[float] = None
    boundary_pct: Optional[float] = None
    fours: int
    sixes: int
    highest_score: Optional[int] = None
    fifties: int
    hundreds: int
    dismissals_by_kind: dict[str, int]
    dismissals_by_phase: dict[str, int]


class BowlerReport(BaseModel):
    player: PlayerOut
    filters: dict
    overall: BowlingStats
    by_phase: dict[str, BowlingStats]


class BatterReport(BaseModel):
    player: PlayerOut
    filters: dict
    overall: BattingStats
    by_phase: dict[str, BattingStats]
