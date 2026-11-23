import { useState } from 'react'
import { Link } from 'react-router-dom'
import Status from '../components/Status.jsx'
import { qs } from '../services/api.js'
import { useApi } from '../services/useApi.js'

const PAGE = 25

export default function Matches() {
  const [form, setForm] = useState({ team: '', tournament: '' })
  const [applied, setApplied] = useState({ team: '', tournament: '' })
  const [offset, setOffset] = useState(0)

  const { data, error, loading } = useApi(`/matches${qs({ ...applied, limit: PAGE, offset })}`)

  function submit(e) {
    e.preventDefault()
    setApplied({ team: form.team.trim(), tournament: form.tournament.trim() })
    setOffset(0)
  }

  return (
    <>
      <h1>Matches</h1>
      <form className="filters" onSubmit={submit}>
        <label>Team
          <input value={form.team} onChange={(e) => setForm({ ...form, team: e.target.value })} placeholder="e.g. Mumbai" />
        </label>
        <label>Tournament
          <input value={form.tournament} onChange={(e) => setForm({ ...form, tournament: e.target.value })} placeholder="e.g. Premier" />
        </label>
        <button type="submit">Filter</button>
      </form>
      <div className="card">
        <Status loading={loading} error={error} />
        {data && data.length === 0 && <p className="muted">No matches found.</p>}
        {data && data.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Date</th><th>Match</th><th>Venue</th><th>Winner</th><th>Tournament</th></tr></thead>
              <tbody>
                {data.map((m) => (
                  <tr key={m.id}>
                    <td>{m.match_date || '–'}</td>
                    <td><Link to={`/matches/${m.id}`}>{m.team1} vs {m.team2}</Link></td>
                    <td>{m.venue || '–'}</td>
                    <td>{m.winner || '–'}</td>
                    <td>{m.tournament || '–'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pager">
          <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))}>Previous</button>
          <span className="muted">Showing {offset + 1}–{offset + (data ? data.length : 0)}</span>
          <button disabled={!data || data.length < PAGE} onClick={() => setOffset(offset + PAGE)}>Next</button>
        </div>
      </div>
    </>
  )
}
