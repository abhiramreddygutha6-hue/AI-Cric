import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api.js'

const EMPTY = { team1: '', team2: '', match_date: '', match_type: 'T20', venue: '', tournament: '', winner: '' }

export default function Upload() {
  const [form, setForm] = useState(EMPTY)
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setResult(null)
    setError(null)
    if (!file) {
      setError('Choose a CSV file first.')
      return
    }
    const fd = new FormData()
    fd.append('file', file)
    Object.entries(form).forEach(([k, v]) => {
      if (v.trim() !== '') fd.append(k, v.trim())
    })
    setBusy(true)
    try {
      setResult(await api.upload('/import/scorecard', fd))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <h1>Upload a scorecard</h1>
      <p className="muted">
        One CSV per match, one row per ball. Required columns: innings, batting_team, over (starts at 1), ball,
        bowler, batter, runs_batter. Optional: non_striker, runs_extras, extra_type, wicket_kind, player_out.
        See <code>docs/sample_scorecard.csv</code>. Team names in the CSV must match team1 / team2 exactly.
      </p>
      <form className="card form" onSubmit={submit}>
        <label>CSV file
          <input type="file" accept=".csv,text/csv" onChange={(e) => setFile(e.target.files[0] || null)} />
        </label>
        <div className="grid-2">
          <label>Team 1 *<input required value={form.team1} onChange={set('team1')} /></label>
          <label>Team 2 *<input required value={form.team2} onChange={set('team2')} /></label>
          <label>Match date *<input required type="date" value={form.match_date} onChange={set('match_date')} /></label>
          <label>Match type
            <select value={form.match_type} onChange={set('match_type')}>
              <option>T20</option><option>ODI</option><option>Test</option>
            </select>
          </label>
          <label>Venue<input value={form.venue} onChange={set('venue')} /></label>
          <label>Tournament<input value={form.tournament} onChange={set('tournament')} /></label>
          <label>Winner
            <select value={form.winner} onChange={set('winner')}>
              <option value="">Not recorded</option>
              {form.team1.trim() && <option value={form.team1}>{form.team1}</option>}
              {form.team2.trim() && <option value={form.team2}>{form.team2}</option>}
            </select>
          </label>
        </div>
        <button type="submit" disabled={busy}>{busy ? 'Uploading…' : 'Upload'}</button>
      </form>

      {error && <p className="error">Error: {error}</p>}
      {result && (
        <p className="success">
          Imported {result.deliveries} deliveries. <Link to={`/matches/${result.match_id}`}>View the match</Link>
        </p>
      )}
    </>
  )
}
