import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthProvider'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  return children
}
