import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Status from '../components/Status.jsx'
import { qs } from '../services/api.js'
import { useApi } from '../services/useApi.js'

export default function Players() {
  const [text, setText] = useState('')
  const [search, setSearch] = useState('')

  // wait for a short pause in typing before searching
  useEffect(() => {
    const t = setTimeout(() => setSearch(text.trim()), 300)
    return () => clearTimeout(t)
  }, [text])

  const { data, error, loading } = useApi(search.length >= 2 ? `/players${qs({ search, limit: 40 })}` : null)

  return (
    <>
      <h1>Players</h1>
      <div className="filters">
        <label>Search by name
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. kohli" autoFocus />
        </label>
      </div>
      <div className="card">
        {search.length < 2 && <p className="muted">Type at least 2 letters. Names follow Cricsheet style, such as “V Kohli”.</p>}
        <Status loading={loading} error={error} />
        {data && data.length === 0 && <p className="muted">No players found.</p>}
        {data && data.length > 0 && (
          <ul className="list">
            {data.map((p) => (
              <li key={p.id}><Link to={`/players/${p.id}`}>{p.name}</Link></li>
            ))}
          </ul>
        )}
      </div>
    </>
  )
}
