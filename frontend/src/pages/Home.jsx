import { Link } from 'react-router-dom'
import ScoreRing from '../components/ScoreRing.jsx'
import Status from '../components/Status.jsx'
import { useApi } from '../services/useApi.js'
import { fmt, pct } from '../services/format.js'

const LEADER_STATS = {
  bowlers: (s) => [['Economy', fmt(s.economy)], ['Wickets', s.wickets], ['Dot balls', pct(s.dot_ball_pct)]],
  batters: (s) => [['Runs', s.runs], ['Strike rate', fmt(s.strike_rate)], ['Average', fmt(s.average)]],
}
const ROW_STAT = {
  bowlers: (s) => `${fmt(s.economy)} economy`,
  batters: (s) => `${s.runs} runs`,
}

function Board({ title, kind }) {
  const { data, error, loading } = useApi(`/rankings/${kind}?limit=6`)
  const lead = data && data[0]
  return (
    <section className="board">
      <h2>{title}</h2>
      <Status loading={loading} error={error} />
      {data && data.length === 0 && <p className="muted">No players yet. Import some matches first.</p>}
      {lead && (
        <div className="leader">
          <ScoreRing score={lead.score} size={92} />
          <div>
            <Link className="leader-name" to={`/players/${lead.player_id}`}>{lead.name}</Link>
            <dl className="leader-stats">
              {LEADER_STATS[kind](lead.stats).map(([label, value]) => (
                <div key={label}><dd>{value}</dd><dt>{label}</dt></div>
              ))}
            </dl>
          </div>
        </div>
      )}
      {data && data.length > 1 && (
        <ol className="rows" start={2}>
          {data.slice(1).map((r) => (
            <li key={r.player_id}>
              <Link to={`/players/${r.player_id}`}>{r.name}</Link>
              <span className="muted">{ROW_STAT[kind](r.stats)}</span>
              <ScoreRing score={r.score} size={34} />
            </li>
          ))}
        </ol>
      )}
      <p><Link to="/rankings">See all rankings</Link></p>
    </section>
  )
}

export default function Home() {
  const matches = useApi('/matches?limit=6')
  return (
    <>
      <h1>Who is performing best?</h1>
      <p className="muted lede">
        Efficiency scores rank every player against the rest of the pool. The first load takes a few seconds while they are calculated.
      </p>
      <div className="grid-2 boards">
        <Board title="Bowlers" kind="bowlers" />
        <Board title="Batters" kind="batters" />
      </div>
      <section className="card">
        <h2>Recent matches</h2>
        <Status loading={matches.loading} error={matches.error} />
        {matches.data && matches.data.length === 0 && <p className="muted">No matches yet. Upload a scorecard or import Cricsheet data.</p>}
        {matches.data && matches.data.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Date</th><th>Match</th><th>Winner</th></tr></thead>
              <tbody>
                {matches.data.map((m) => (
                  <tr key={m.id}>
                    <td>{m.match_date || '–'}</td>
                    <td><Link to={`/matches/${m.id}`}>{m.team1} vs {m.team2}</Link></td>
                    <td>{m.winner || '–'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}
