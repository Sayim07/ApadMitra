import React, { useEffect, useMemo, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import Button from './Button'

export default function Navbar({ user, profile, profileLoaded, loading, onLogout }) {
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

  const role = profile?.role
  const isAuthResolving = Boolean(loading || (user && !profileLoaded))
  const isSignedIn = Boolean(user)
  const effectiveRole = role || (isSignedIn ? 'CITIZEN' : null)
  const dashboardPath = effectiveRole && effectiveRole !== 'CITIZEN' ? '/dashboard' : '/me'
  const dashboardLabel = effectiveRole && effectiveRole !== 'CITIZEN' ? 'Dashboard' : 'My Dashboard'
  const showDashboard = isSignedIn
  const displayName = profile?.name || profile?.user_id || user?.email || user?.uid

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
          {showDashboard ? (
            <NavLink to={dashboardPath} className={({ isActive }) => (isActive ? 'ui-nav-link ui-nav-link-active' : 'ui-nav-link')}>
              {dashboardLabel}
            </NavLink>
          ) : null}
        </nav>

        <div className="ui-navbar-right">
          {isAuthResolving ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="ui-spinner" aria-label="Loading" />
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>Signing in…</div>
            </div>
          ) : isSignedIn ? (
            <div className="ui-user">
              <div className="ui-avatar" aria-hidden="true">{initials}</div>
              <div className="ui-user-meta">
                <div className="ui-user-name">{displayName}</div>
                <div className="ui-user-role">{effectiveRole}</div>
              </div>
              <Button variant="ghost" size="sm" onClick={onLogout}>Sign out</Button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <Button as={Link} to="/login/user" variant="primary" size="sm">
                Get Started Free
              </Button>
              <Button as={Link} to="/login/authority" variant="outline" size="sm">
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
            {showDashboard ? (
              <NavLink to={dashboardPath} className="ui-mobile-link" onClick={() => setOpen(false)}>{dashboardLabel}</NavLink>
            ) : null}
            <div className="ui-mobile-divider" />
            {isAuthResolving ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 2px' }}>
                <span className="ui-spinner" aria-label="Loading" />
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>Signing in…</div>
              </div>
            ) : isSignedIn ? (
              <Button variant="ghost" size="md" onClick={() => { setOpen(false); onLogout?.() }}>
                Sign out
              </Button>
            ) : (
              <>
                <Button as={Link} to="/login/user" variant="primary" size="md" onClick={() => setOpen(false)}>
                  Get Started Free
                </Button>
                <Button as={Link} to="/login/authority" variant="outline" size="md" onClick={() => setOpen(false)}>
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
