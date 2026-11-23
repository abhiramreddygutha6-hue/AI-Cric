import { Link } from 'react-router-dom'
import { fmt, pct } from '../services/format.js'

export default function MatchupTable({ title, opponentLabel, rows }) {
  if (!rows || !rows.length) return null
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>{opponentLabel}</th><th>Balls</th><th>Runs</th><th>Dismissals</th>
              <th>Strike rate</th><th>Dot %</th><th>Boundary %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.opponent_id}>
                <td><Link to={`/players/${r.opponent_id}`}>{r.opponent_name}</Link></td>
                <td>{r.balls}</td><td>{r.runs}</td><td>{r.dismissals}</td>
                <td>{fmt(r.strike_rate)}</td><td>{pct(r.dot_ball_pct)}</td><td>{pct(r.boundary_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
