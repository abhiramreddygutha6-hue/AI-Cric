import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.dirname(__file__))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import func, select
from app.database import Base, SessionLocal, engine
from app.models import Delivery, Match, Player, Team
from app.services.cricsheet import parse_match
from app.services.importer import Cache, save_parsed_match
from fixtures import sample_cricsheet_match


def test_import_and_idempotent():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        pm = parse_match(sample_cricsheet_match(), "m1")
        mid = save_parsed_match(db, pm, Cache.load(db))
        db.commit()
        assert mid is not None
        assert db.scalar(select(func.count()).select_from(Delivery)) == 5
        assert db.scalar(select(func.count()).select_from(Team)) == 2
        assert db.scalar(select(func.count()).select_from(Player)) == 3
        # importing the same match again is a no-op
        assert save_parsed_match(db, pm, Cache.load(db)) is None
        assert db.scalar(select(func.count()).select_from(Match)) == 1
