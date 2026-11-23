import { Link, useParams } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Status from '../components/Status.jsx'
import { useApi } from '../services/useApi.js'

export default function MatchDetail() {
  const { id } = useParams()
  const { data: m, error, loading } = useApi(`/matches/${id}`)
  if (loading || error) return <Status loading={loading} error={error} />

  const chart = m.innings.map((i) => ({ name: `${i.batting_team || 'Innings ' + i.innings} (${i.innings})`, runs: i.runs }))

  return (
    <>
      <p><Link to="/matches">All matches</Link></p>
      <h1>{m.team1} vs {m.team2}</h1>
      <p className="muted">
        {[m.tournament, m.venue, m.match_date, m.match_type].filter(Boolean).join(', ')}
      </p>
      <p><strong>{m.winner ? `Winner: ${m.winner}` : 'No winner recorded'}</strong></p>

      <div className="card">
        <h3>Innings</h3>
        <table className="table">
          <thead><tr><th>Innings</th><th>Batting team</th><th>Score</th><th>Overs</th></tr></thead>
          <tbody>
            {m.innings.map((i) => (
              <tr key={i.innings}>
                <td>{i.innings}</td>
                <td>{i.batting_team || '–'}</td>
                <td>{i.runs}/{i.wickets}</td>
                <td>{Math.floor(i.legal_balls / 6)}.{i.legal_balls % 6}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted">{m.deliveries_count} deliveries recorded.</p>
      </div>

      {chart.length > 0 && (
        <div className="card chart">
          <h4>Runs by innings</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="runs" fill="#1f6b4a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </>
  )
}
