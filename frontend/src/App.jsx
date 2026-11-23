import { Link, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import Rankings from './pages/Rankings.jsx'
import Players from './pages/Players.jsx'
import PlayerDetail from './pages/PlayerDetail.jsx'
import Matches from './pages/Matches.jsx'
import MatchDetail from './pages/MatchDetail.jsx'
import Upload from './pages/Upload.jsx'

function NotFound() {
  return (
    <div className="card">
      <h2>Page not found</h2>
      <p><Link to="/">Back to the dashboard</Link></p>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="rankings" element={<Rankings />} />
        <Route path="players" element={<Players />} />
        <Route path="players/:id" element={<PlayerDetail />} />
        <Route path="matches" element={<Matches />} />
        <Route path="matches/:id" element={<MatchDetail />} />
        <Route path="upload" element={<Upload />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
