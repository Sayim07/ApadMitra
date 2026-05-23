import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthProvider'

export default function CitizenRoute({ children }) {
  const { user, profile, profileLoaded, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login/user" replace state={{ from: location }} />
  if (!profileLoaded) return <div>Loading...</div>
  if (profile?.role && profile.role !== 'CITIZEN') return <Navigate to="/dashboard" replace />
  return children
}
