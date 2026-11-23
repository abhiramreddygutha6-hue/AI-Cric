export default function Status({ loading, error }) {
  if (loading) return <p className="muted">Loading…</p>
  if (error) return <p className="error">Error: {error}</p>
  return null
}
