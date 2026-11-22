import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import inspect
from app.database import Base, engine
import app.models  # noqa


def test_tables_created():
    Base.metadata.create_all(bind=engine)
    names = set(inspect(engine).get_table_names())
    assert {"teams", "players", "tournaments", "matches", "videos",
            "deliveries", "batting_events", "fielding_events"} <= names
