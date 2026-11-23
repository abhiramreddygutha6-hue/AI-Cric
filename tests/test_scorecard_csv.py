import csv, io, os, sys
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.scorecard import csv_rows_to_match

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "docs", "sample_scorecard.csv")
META = dict(team1="Team A", team2="Team B", match_date=date(2026, 2, 1), match_type="T20",
            venue="Ground", tournament=None, winner="Team A")


def _rows():
    with open(SAMPLE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_sample_csv_parses():
    pm = csv_rows_to_match(_rows(), META)
    assert len(pm["deliveries"]) == 6
    assert pm["deliveries"][0]["over_no"] == 0          # CSV over 1 -> 0-based
    assert pm["deliveries"][1]["extra_type"] == "wides"
    assert pm["deliveries"][3]["is_wicket"] and pm["deliveries"][3]["player_out"] == "Batter Two"
    assert pm["source_id"] == "csv-2026-02-01-team-a-team-b"


def _expect_error(rows, meta, text):
    try:
        csv_rows_to_match(rows, meta)
    except ValueError as e:
        assert text in str(e), str(e)
        return
    raise AssertionError("expected ValueError")


def test_bad_inputs():
    _expect_error([], META, "no data rows")
    _expect_error([{"innings": "1"}], META, "missing column")
    rows = _rows(); rows[0]["batting_team"] = "Team Z"
    _expect_error(rows, META, "batting_team")
    rows = _rows(); rows[0]["over"] = "0"
    _expect_error(rows, META, "starts at 1")
    rows = _rows(); rows[0]["extra_type"] = "oops"
    _expect_error(rows, META, "extra_type")
    _expect_error(_rows(), dict(META, winner="Team Z"), "winner")
