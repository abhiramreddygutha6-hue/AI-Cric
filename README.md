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

## Week 3: stats endpoints
- `GET /stats/bowlers/{player_id}`: balls, overs, runs, wickets, economy, average, strike rate, dot-ball %, boundary %, plus a `by_phase` split.
- `GET /stats/batters/{player_id}`: innings, runs, average, strike rate, dot-ball %, boundary %, 4s/6s, highest score, 50s/100s, dismissals by kind, plus `by_phase`.
- Optional filters on both: `phase` (powerplay/middle/death), `tournament`, `season` (year).
- Find a player id with `GET /players?search=bumrah`.
- Scoring rules are documented at the top of `backend/app/services/stats.py`.

## Week 4: rankings and matchups
- `GET /rankings/bowlers` and `GET /rankings/batters`: efficiency score (0-100) with per-metric components. Options: `min_balls` (default 120), `limit`, `phase`, `tournament`, `season`.
  - Bowler score: economy 35%, strike rate 25%, dot-ball % 25%, boundary % 15%.
  - Batter score: strike rate 30%, average 30%, boundary % 20%, dot-ball % 20% (lower is better).
  - Each metric is a percentile rank among qualified players, so a score is relative to the pool the filters create.
- `GET /matchups?bowler_id=&batter_id=`: head-to-head, overall and by phase.
- `GET /matchups/bowler/{id}` and `GET /matchups/batter/{id}`: how each opponent has fared (`min_balls`, `sort`, `limit`).
- Rankings are cached for 5 minutes and cleared after a scorecard upload. After using the CLI importer, restart the server.

## Week 5: dashboard (React)
Needs Node.js 20 or newer. With the backend running on port 8000:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Pages: Dashboard, Rankings (filters: bowlers/batters, phase, season, min balls), Players (search), player detail (stats, phase charts, matchups), Matches and match detail, Upload (scorecard CSV).
The dev server forwards `/api/...` to the backend, so there is no CORS setup. The AI chat panel is added in Week 6.
