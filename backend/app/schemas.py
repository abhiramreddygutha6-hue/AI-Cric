from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cricsheet_id: Optional[str] = None
    batting_hand: Optional[str] = None
    bowling_style: Optional[str] = None


class MatchOut(BaseModel):
    id: int
    source_id: Optional[str] = None
    tournament: Optional[str] = None
    team1: str
    team2: str
    venue: Optional[str] = None
    match_date: Optional[date] = None
    match_type: Optional[str] = None
    winner: Optional[str] = None


class InningsSummary(BaseModel):
    innings: int
    batting_team: Optional[str] = None
    runs: int
    wickets: int
    legal_balls: int


class MatchDetail(MatchOut):
    deliveries_count: int
    innings: list[InningsSummary]
