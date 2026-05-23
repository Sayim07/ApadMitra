import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthProvider'

export default function AuthorityRoute({ children }) {
  const { user, profile, profileLoaded, profileError, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login/authority" replace state={{ from: location }} />
  if (!profileLoaded) return <div>Loading...</div>
  if (!profile && profileError === 'network') {
    return (
      <div style={{ padding: 24, fontFamily: 'var(--font-mono)' }}>
        Backend profile sync failed. Make sure the backend is running on http://localhost:8000 and refresh.
      </div>
    )
  }
  if (!profile?.role) return <Navigate to="/authority-apply" replace />
  if (profile.role === 'CITIZEN') return <Navigate to="/me" replace />
  return children
}
