import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { PHASES } from '../services/format.js'

export default function PhaseChart({ byPhase, metric, label, color = '#1f6b4a' }) {
  const data = PHASES.filter((p) => byPhase && byPhase[p])
    .map((p) => ({ phase: p, value: byPhase[p][metric] }))
    .filter((d) => d.value !== null && d.value !== undefined)

  if (!data.length) return <p className="muted">No data for “{label}”.</p>

  return (
    <div className="chart">
      <h4>{label}</h4>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="phase" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" name={label} fill={color} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
