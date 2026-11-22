# API Endpoints (draft)

| Method | Path | Purpose | Week |
|---|---|---|---|
| GET | /health | Liveness check | 1 |
| GET | /matches, /matches/{id} | List and fetch matches | 2 |
| GET | /players, /players/{id} | Search and fetch players | 2 |
| GET | /teams | List teams | 2 |
| POST | /import/scorecard | Upload scorecard CSV | 2 |
| GET | /stats/bowlers/{id}?phase=&vs_hand= | Bowling stats | 3 |
| GET | /stats/batters/{id}?phase=&vs_type= | Batting stats | 3 |
| GET | /stats/matchup?bowler=&batter= | Matchup table | 4 |
| GET | /rankings/bowlers, /rankings/batters | Efficiency scores | 4 |
| POST | /chat | Chatbot message with tool calling | 6 |
| POST | /videos | Upload video, returns job id | 7 |
| GET | /videos/{id}/status | Processing status | 7 |
| GET | /videos/{id}/deliveries | Per-delivery video data | 10-12 |
| GET | /predict/matchup, /predict/risks | Predictions | 17 |
