import { useState } from 'react'
import { Link } from 'react-router-dom'
import ScoreRing from '../components/ScoreRing.jsx'
import Status from '../components/Status.jsx'
import { qs } from '../services/api.js'
import { useApi } from '../services/useApi.js'
import { fmt, pct, SEASONS } from '../services/format.js'

const BOWLER_COLS = [
  ['Overs', (s) => s.overs], ['Wkts', (s) => s.wickets], ['Econ', (s) => fmt(s.economy)],
  ['SR', (s) => fmt(s.strike_rate)], ['Dot %', (s) => pct(s.dot_ball_pct)], ['Bdry %', (s) => pct(s.boundary_pct)],
]
const BATTER_COLS = [
  ['Runs', (s) => s.runs], ['Avg', (s) => fmt(s.average)], ['SR', (s) => fmt(s.strike_rate)],
  ['Dot %', (s) => pct(s.dot_ball_pct)], ['Bdry %', (s) => pct(s.boundary_pct)],
  ['4s', (s) => s.fours], ['6s', (s) => s.sixes],
]

export default function Rankings() {
  const [kind, setKind] = useState('bowlers')
  const [phase, setPhase] = useState('')
  const [season, setSeason] = useState('')
  const [minBalls, setMinBalls] = useState(120)

  const path = `/rankings/${kind}${qs({ limit: 30, min_balls: minBalls, phase, season })}`
  const { data, error, loading } = useApi(path)
  const cols = kind === 'bowlers' ? BOWLER_COLS : BATTER_COLS

  return (
    <>
      <h1>Rankings</h1>
      <div className="filters">
        <div className="tabs">
          <button className={kind === 'bowlers' ? 'active' : ''} onClick={() => setKind('bowlers')}>Bowlers</button>
          <button className={kind === 'batters' ? 'active' : ''} onClick={() => setKind('batters')}>Batters</button>
        </div>
        <label>Phase
          <select value={phase} onChange={(e) => setPhase(e.target.value)}>
            <option value="">All</option>
            <option value="powerplay">Powerplay</option>
            <option value="middle">Middle</option>
            <option value="death">Death</option>
          </select>
        </label>
        <label>Season
          <select value={season} onChange={(e) => setSeason(e.target.value)}>
            <option value="">All</option>
            {SEASONS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </label>
        <label>Min balls
          <select value={minBalls} onChange={(e) => setMinBalls(Number(e.target.value))}>
            {[30, 60, 120, 240, 480].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
      </div>
      <p className="muted">
        Score (0–100) combines percentile ranks of the metrics shown among players with at least {minBalls} balls
        {kind === 'bowlers' ? ' (economy, strike rate, dot-ball %, boundary %).' : ' (strike rate, average, boundary %, dot-ball %).'}
      </p>
      <div className="card">
        <Status loading={loading} error={error} />
        {data && data.length === 0 && <p className="muted">No players match these filters.</p>}
        {data && data.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>#</th><th>Player</th><th>Score</th>{cols.map(([label]) => <th key={label}>{label}</th>)}</tr>
              </thead>
              <tbody>
                {data.map((r) => (
                  <tr key={r.player_id} title={Object.entries(r.components).map(([k, v]) => `${k}: ${v}`).join('  |  ')}>
                    <td>{r.rank}</td>
                    <td><Link to={`/players/${r.player_id}`}>{r.name}</Link></td>
                    <td><ScoreRing score={r.score} size={38} /></td>
                    {cols.map(([label, get]) => <td key={label}>{get(r.stats)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}
