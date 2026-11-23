# CRICKET-IQ

Cricket analytics system: bowling, batting and fielding analysis from scorecard data and match video, with an AI assistant that suggests plans for upcoming matches and tournaments.

## Structure
- `backend/`: FastAPI, SQLAlchemy models, routes, services
- `frontend/`: React dashboard and chat UI (from Week 5)
- `ai_engine/`: video processing, detection, tracking, batting/bowling/fielding analysis, prediction
- `chatbot/`: knowledge base, retrieval, assistant
- `data/`, `storage/`: Cricsheet data and uploaded videos (git-ignored)
- `docs/`: features, API draft, schema notes

## Run (Week 1)
```bash
cp .env.example .env        # set a real POSTGRES_PASSWORD, and use it in DATABASE_URL too
docker compose up --build
# open http://localhost:8000/health  and  http://localhost:8000/docs
```
Tables are created automatically on startup.

## Explore data
Download JSON from https://cricsheet.org/downloads/ into `data/cricsheet/`, then:
```bash
python scripts/explore_cricsheet.py data/cricsheet
```

## Tests
```bash
pip install -r backend/requirements.txt
pytest tests
```

## Schedule
See the 18-week plan. Week 1 = setup, design, schema, data exploration.

## Week 2: import data and use the API
Cricsheet files go in `data/cricsheet/`. Reset the DB once if you ran Week 1 (a column was added):
```bash
docker compose down -v && docker compose up --build -d
docker compose exec backend python -m app.cli_import /data/cricsheet --limit 200   # drop --limit for everything
```
Then open http://localhost:8000/docs and try `GET /matches`, `GET /matches/{id}`, `GET /players?search=kohli`, `GET /teams`.

Upload your own match: `POST /import/scorecard` with a CSV (see `docs/sample_scorecard.csv`; `over` starts at 1) plus team1, team2 and match_date.
