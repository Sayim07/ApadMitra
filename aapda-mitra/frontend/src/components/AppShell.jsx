import React from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'

export default function AppShell({ children, title, description, actions }) {
  const { profile, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    if (location.pathname.startsWith('/dashboard')) navigate('/')
  }

  return (
    <div>
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand">
            <div className="brand-mark" aria-hidden="true" />
            <div className="brand-name">AapdaMitra</div>
          </Link>

          <nav className="nav" aria-label="Primary navigation">
            <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'active' : undefined)}>Dashboard</NavLink>
            <NavLink to="/report" className={({ isActive }) => (isActive ? 'active' : undefined)}>Report</NavLink>
            <NavLink to="/sos" className={({ isActive }) => (isActive ? 'active' : undefined)}>SOS</NavLink>
          </nav>

          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            {profile ? (
              <>
                <div style={{ display: 'grid', lineHeight: 1.15 }}>
                  <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: 13 }}>
                    {profile.name || profile.user_id}
                  </span>
                  <span className="muted-2" style={{ fontSize: 12 }}>
                    {profile.role}
                  </span>
                </div>
                <button className="btn btn-ghost" onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : (
              <Link className="btn btn-primary" to="/login">
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="container">
        {(title || description || actions) && (
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
            <div style={{ display: 'grid', gap: 6 }}>
              {title && <h2 style={{ fontSize: 24 }}>{title}</h2>}
              {description && <p>{description}</p>}
            </div>
            {actions && <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>{actions}</div>}
          </div>
        )}
        <div style={{ height: 18 }} />
        {children}
      </main>
    </div>
  )
}
