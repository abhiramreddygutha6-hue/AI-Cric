import { Link, NavLink, Outlet } from 'react-router-dom'
import ChatPanel from './ChatPanel.jsx'
import Logo from './Logo.jsx'

const links = [
  ['/', 'Dashboard'],
  ['/rankings', 'Rankings'],
  ['/players', 'Players'],
  ['/matches', 'Matches'],
  ['/upload', 'Upload'],
]

export default function Layout() {
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand"><Logo /><span>AiCric</span></Link>
          <nav>
            {links.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => (isActive ? 'active' : '')}>
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
      <ChatPanel />
    </>
  )
}
