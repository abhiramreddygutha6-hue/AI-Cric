import { useState } from 'react'
import { useParams } from 'react-router-dom'
import MatchupTable from '../components/MatchupTable.jsx'
import PhaseChart from '../components/PhaseChart.jsx'
import StatCard from '../components/StatCard.jsx'
import Status from '../components/Status.jsx'
import { qs } from '../services/api.js'
import { useApi } from '../services/useApi.js'
import { fmt, pct, SEASONS } from '../services/format.js'

export default function PlayerDetail() {
  const { id } = useParams()
  const [season, setSeason] = useState('')

  const player = useApi(`/players/${id}`)
  const bowl = useApi(`/stats/bowlers/${id}${qs({ season })}`)
  const bat = useApi(`/stats/batters/${id}${qs({ season })}`)
  const bowlM = useApi(`/matchups/bowler/${id}${qs({ limit: 10, season })}`)
  const batM = useApi(`/matchups/batter/${id}${qs({ limit: 10, season })}`)

  if (player.loading || player.error) return <Status loading={player.loading} error={player.error} />

  const b = bowl.data && bowl.data.overall
  const t = bat.data && bat.data.overall
  const hasBowling = b && b.balls > 0
  const hasBatting = t && t.balls > 0

  return (
    <>
      <h1>{player.data.name}</h1>
      <div className="filters">
        <label>Season
          <select value={season} onChange={(e) => setSeason(e.target.value)}>
            <option value="">All seasons</option>
            {SEASONS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </label>
      </div>

      <Status loading={bowl.loading || bat.loading} error={bowl.error || bat.error} />
      {!bowl.loading && !bat.loading && !hasBowling && !hasBatting && (
        <p className="muted">No bowling or batting data for this player{season ? ` in ${season}` : ''}.</p>
      )}

      {hasBatting && (
        <div className="card">
          <h2>Batting</h2>
          <div className="stats">
            <StatCard label="Innings" value={t.innings} />
            <StatCard label="Runs" value={t.runs} />
            <StatCard label="Average" value={fmt(t.average)} />
            <StatCard label="Strike rate" value={fmt(t.strike_rate)} />
            <StatCard label="Highest" value={fmt(t.highest_score)} />
            <StatCard label="50s / 100s" value={`${t.fifties} / ${t.hundreds}`} />
            <StatCard label="4s / 6s" value={`${t.fours} / ${t.sixes}`} />
            <StatCard label="Dot ball %" value={pct(t.dot_ball_pct)} />
            <StatCard label="Boundary %" value={pct(t.boundary_pct)} />
            <StatCard label="Not outs" value={fmt(t.not_outs)} />
          </div>
          <div className="grid-2">
            <PhaseChart byPhase={bat.data.by_phase} metric="strike_rate" label="Strike rate by phase" />
            <PhaseChart byPhase={bat.data.by_phase} metric="runs" label="Runs by phase" color="#b8963e" />
          </div>
          {Object.keys(t.dismissals_by_kind).length > 0 && (
            <p className="muted">
              Dismissals:{' '}
              {Object.entries(t.dismissals_by_kind).sort((a, c) => c[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', ')}
            </p>
          )}
        </div>
      )}

      {hasBowling && (
        <div className="card">
          <h2>Bowling</h2>
          <div className="stats">
            <StatCard label="Overs" value={b.overs} />
            <StatCard label="Wickets" value={b.wickets} />
            <StatCard label="Economy" value={fmt(b.economy)} />
            <StatCard label="Average" value={fmt(b.average)} />
            <StatCard label="Strike rate" value={fmt(b.strike_rate)} />
            <StatCard label="Dot ball %" value={pct(b.dot_ball_pct)} />
            <StatCard label="Boundary %" value={pct(b.boundary_pct)} />
            <StatCard label="Wides / no-balls" value={`${b.wides} / ${b.no_balls}`} />
          </div>
          <div className="grid-2">
            <PhaseChart byPhase={bowl.data.by_phase} metric="economy" label="Economy by phase" color="#a4262c" />
            <PhaseChart byPhase={bowl.data.by_phase} metric="wickets" label="Wickets by phase" color="#123d2b" />
          </div>
        </div>
      )}

      {hasBowling && <MatchupTable title="Most faced batters" opponentLabel="Batter" rows={bowlM.data} />}
      {hasBatting && <MatchupTable title="Most faced bowlers" opponentLabel="Bowler" rows={batM.data} />}
    </>
  )
}
