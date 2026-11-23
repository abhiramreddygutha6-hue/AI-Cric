import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cricsheet import parse_match, phase_for
from fixtures import sample_cricsheet_match


def test_parse_basic_fields():
    pm = parse_match(sample_cricsheet_match(), "123")
    assert pm["team1"] == "Team X" and pm["winner"] == "Team X"
    assert pm["tournament"] == "Test League" and pm["match_type"] == "T20"
    assert str(pm["match_date"]) == "2026-01-05"
    assert pm["registry"]["Bowl One"] == "w1"


def test_super_over_skipped_and_counts():
    pm = parse_match(sample_cricsheet_match(), "123")
    assert len(pm["deliveries"]) == 5          # 4 + 1, super over excluded
    assert {d["innings"] for d in pm["deliveries"]} == {1, 2}


def test_extras_wickets_phases():
    ds = parse_match(sample_cricsheet_match(), "123")["deliveries"]
    assert ds[1]["extra_type"] == "wides" and ds[1]["runs_total"] == 1
    assert ds[2]["is_wicket"] and ds[2]["wicket_kind"] == "bowled" and ds[2]["player_out"] == "Bat One"
    assert ds[0]["phase"] == "powerplay" and ds[3]["phase"] == "death"


def test_phase_for():
    assert phase_for("T20", 5) == "powerplay" and phase_for("T20", 6) == "middle"
    assert phase_for("T20", 16) == "death" and phase_for("ODI", 39) == "middle"
    assert phase_for("Test", 3) is None
