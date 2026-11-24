# AiCric: Features and User Flows (Week 1)

## Users
Coach or analyst of one team preparing for a tournament.

## Core flows
1. **Import data**: load Cricsheet history, or upload a scorecard CSV for own matches. (Week 2)
2. **View analysis**: pick a player or team, see bowling, batting and (later) fielding stats with phase and opponent filters. (Weeks 3-5)
3. **Rank**: bowler and batter efficiency scores, bowler-vs-batter matchups. (Week 4)
4. **Ask the AI**: chat box answers questions and suggests plans, using tool calls on the stats DB, never invented numbers. (Week 6)
5. **Upload video**: video is processed in the background; show annotated playback and per-delivery data. (Weeks 7-12)
6. **Plan**: tournament risk report and next-match approach. (Weeks 17-18)

## Pages (frontend)
- Dashboard (team overview, top bowlers/batters)
- Player page (stats, phase splits, matchups, later pitch map and weakness map)
- Match page (scorecard, delivery list, video playback)
- Upload page (scorecard CSV, video)
- Chat panel (docked on every page)

## Out of scope for the first release
Live streaming input, multi-camera sync, mobile app.
