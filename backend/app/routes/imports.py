import csv
import io
from datetime import date
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.importer import Cache, save_parsed_match
from app.services.scorecard import csv_rows_to_match

router = APIRouter(tags=["import"])


@router.post("/import/scorecard")
async def import_scorecard(
    file: UploadFile = File(..., description="CSV with one row per ball"),
    team1: str = Form(...),
    team2: str = Form(...),
    match_date: date = Form(...),
    match_type: str = Form("T20"),
    venue: str | None = Form(None),
    tournament: str | None = Form(None),
    winner: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        text = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "the file must be a UTF-8 CSV")
    rows = list(csv.DictReader(io.StringIO(text)))
    meta = dict(team1=team1, team2=team2, match_date=match_date, match_type=match_type,
                venue=venue, tournament=tournament, winner=winner)
    try:
        pm = csv_rows_to_match(rows, meta)
        match_id = save_parsed_match(db, pm, Cache.load(db))
        if match_id is None:
            db.rollback()
            raise HTTPException(409, "this match was already imported")
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    return {"match_id": match_id, "deliveries": len(pm["deliveries"])}
