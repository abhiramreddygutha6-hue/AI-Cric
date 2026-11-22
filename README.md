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
