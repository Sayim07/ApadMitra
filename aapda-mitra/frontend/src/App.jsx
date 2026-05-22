import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import CitizenReportPage from './pages/CitizenReportPage'
import SOSPage from './pages/SOSPage'
import Dashboard from './pages/Dashboard'
import IncidentDetail from './pages/IncidentDetail'
import Login from './pages/Login'
import AuthProvider from './components/AuthProvider'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path='/' element={<LandingPage />} />
          <Route path='/login' element={<Login />} />
          <Route path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path='/incidents/:id' element={<IncidentDetail />} />
          <Route path='/report' element={<CitizenReportPage />} />
          <Route path='/sos' element={<SOSPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
