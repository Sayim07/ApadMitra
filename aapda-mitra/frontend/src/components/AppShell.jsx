import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'
import Navbar from './ui/Navbar'

export default function AppShell({ children, title, description, actions }) {
  const { user, profile, profileLoaded, logout, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    if (location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/me')) navigate('/')
  }

  return (
    <div>
      <Navbar user={user} profile={profile} profileLoaded={profileLoaded} loading={loading} onLogout={handleLogout} />

      <main className="ui-container">
        {(title || description || actions) && (
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div style={{ display: 'grid', gap: 8 }}>
              {title && <h2 style={{ fontSize: 28, margin: 0 }}>{title}</h2>}
              {description && <p style={{ margin: 0 }}>{description}</p>}
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
