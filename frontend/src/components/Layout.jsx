import { NavLink, Outlet } from 'react-router-dom'

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
          <span className="brand">CRICKET-IQ</span>
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
    </>
  )
}
