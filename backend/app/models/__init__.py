from datetime import date
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, Float, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    cricsheet_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    batting_hand: Mapped[Optional[str]] = mapped_column(String(10))   # right / left
    bowling_style: Mapped[Optional[str]] = mapped_column(String(30))  # pace / off-spin / ...


class Tournament(Base):
    __tablename__ = "tournaments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(30), unique=True)  # Cricsheet file id
    tournament_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tournaments.id"))
    team1_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    team2_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    venue: Mapped[Optional[str]] = mapped_column(String(150))
    match_date: Mapped[Optional[date]] = mapped_column(Date)
    match_type: Mapped[Optional[str]] = mapped_column(String(10))  # T20 / ODI / Test
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))


class Video(Base):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[Optional[int]] = mapped_column(ForeignKey("matches.id"))
    path: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded/processing/done/failed
    fps: Mapped[Optional[float]] = mapped_column(Float)


class Delivery(Base):
    """One row per ball. Scorecard columns come from Cricsheet (Week 2);
    the video columns are filled later by ai_engine (Weeks 10-12)."""
    __tablename__ = "deliveries"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    innings: Mapped[int] = mapped_column(Integer)
    over_no: Mapped[int] = mapped_column(Integer)          # 0-based
    ball_no: Mapped[int] = mapped_column(Integer)          # position within over
    bowler_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    batter_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    non_striker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    runs_batter: Mapped[int] = mapped_column(Integer, default=0)
    runs_extras: Mapped[int] = mapped_column(Integer, default=0)
    runs_total: Mapped[int] = mapped_column(Integer, default=0)
    extra_type: Mapped[Optional[str]] = mapped_column(String(20))  # wides / noballs / byes / legbyes
    is_wicket: Mapped[bool] = mapped_column(Boolean, default=False)
    wicket_kind: Mapped[Optional[str]] = mapped_column(String(30))
    player_out_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    phase: Mapped[Optional[str]] = mapped_column(String(12))       # powerplay / middle / death
    # --- filled by video analysis later ---
    video_id: Mapped[Optional[int]] = mapped_column(ForeignKey("videos.id"))
    release_frame: Mapped[Optional[int]] = mapped_column(Integer)
    speed_kmph: Mapped[Optional[float]] = mapped_column(Float)
    pitch_x: Mapped[Optional[float]] = mapped_column(Float)        # line (across the pitch)
    pitch_y: Mapped[Optional[float]] = mapped_column(Float)        # length (along the pitch)
    line: Mapped[Optional[str]] = mapped_column(String(20))
    length: Mapped[Optional[str]] = mapped_column(String(20))


class BattingEvent(Base):
    __tablename__ = "batting_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id"), index=True)
    shot_type: Mapped[Optional[str]] = mapped_column(String(20))   # drive / pull / cut / sweep / defence / leave
    footwork: Mapped[Optional[str]] = mapped_column(String(20))    # front / back
    direction_deg: Mapped[Optional[float]] = mapped_column(Float)
    control: Mapped[Optional[bool]] = mapped_column(Boolean)


class FieldingEvent(Base):
    __tablename__ = "fielding_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id"), index=True)
    fielder_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    event_type: Mapped[str] = mapped_column(String(20))            # catch / drop / stop / throw / misfield
    position_x: Mapped[Optional[float]] = mapped_column(Float)
    position_y: Mapped[Optional[float]] = mapped_column(Float)
    throw_speed_kmph: Mapped[Optional[float]] = mapped_column(Float)
    runs_saved: Mapped[Optional[float]] = mapped_column(Float)
