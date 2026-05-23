import React, { useEffect, useMemo, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import Button from './Button'

export default function Navbar({ profile, onLogout }) {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const initials = useMemo(() => {
    const name = (profile?.name || profile?.user_id || '').toString().trim()
    if (!name) return 'U'
    const parts = name.split(/\s+/).filter(Boolean)
    const letters = parts.slice(0, 2).map(p => p[0]?.toUpperCase()).join('')
    return letters || 'U'
  }, [profile])

  return (
    <header className={['ui-navbar', scrolled ? 'ui-navbar-scrolled' : undefined].filter(Boolean).join(' ')}>
      <div className="ui-navbar-inner">
        <Link to="/" className="ui-logo" onClick={() => setOpen(false)}>
          <span className="ui-logo-bolt" aria-hidden="true">⚡</span>
          <span className="ui-logo-text">
            <span className="ui-logo-accent">Aapda</span>Mitra
          </span>
        </Link>

        <nav className="ui-nav" aria-label="Primary navigation">
          <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'ui-nav-link ui-nav-link-active' : 'ui-nav-link')}>
            Dashboard
          </NavLink>
          <NavLink to="/report" className={({ isActive }) => (isActive ? 'ui-nav-link ui-nav-link-active' : 'ui-nav-link')}>
            Report
          </NavLink>
          <NavLink to="/sos" className={({ isActive }) => (isActive ? 'ui-nav-link ui-nav-link-active' : 'ui-nav-link')}>
            SOS
          </NavLink>
        </nav>

        <div className="ui-navbar-right">
          {profile ? (
            <div className="ui-user">
              <div className="ui-avatar" aria-hidden="true">{initials}</div>
              <div className="ui-user-meta">
                <div className="ui-user-name">{profile.name || profile.user_id}</div>
                <div className="ui-user-role">{profile.role}</div>
              </div>
              <Button variant="ghost" size="sm" onClick={onLogout}>Sign out</Button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <Button as={Link} to="/login" variant="primary" size="sm">
                Get Started Free
              </Button>
              <Button as={Link} to="/login" variant="outline" size="sm">
                Authority Login →
              </Button>
            </div>
          )}

          <button className="ui-burger" type="button" aria-label="Open menu" onClick={() => setOpen(v => !v)}>
            <span className="ui-burger-bar" />
            <span className="ui-burger-bar" />
            <span className="ui-burger-bar" />
          </button>
        </div>
      </div>

      {open ? (
        <div className="ui-mobile-drawer" role="dialog" aria-modal="true">
          <div className="ui-mobile-drawer-inner">
            <NavLink to="/dashboard" className="ui-mobile-link" onClick={() => setOpen(false)}>Dashboard</NavLink>
            <NavLink to="/report" className="ui-mobile-link" onClick={() => setOpen(false)}>Report</NavLink>
            <NavLink to="/sos" className="ui-mobile-link" onClick={() => setOpen(false)}>SOS</NavLink>
            <div className="ui-mobile-divider" />
            {profile ? (
              <Button variant="ghost" size="md" onClick={() => { setOpen(false); onLogout?.() }}>
                Sign out
              </Button>
            ) : (
              <>
                <Button as={Link} to="/login" variant="primary" size="md" onClick={() => setOpen(false)}>
                  Get Started Free
                </Button>
                <Button as={Link} to="/login" variant="outline" size="md" onClick={() => setOpen(false)}>
                  Authority Login →
                </Button>
              </>
            )}
          </div>
        </div>
      ) : null}
    </header>
  )
}
