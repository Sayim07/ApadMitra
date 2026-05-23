import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import CitizenReportPage from './pages/CitizenReportPage'
import SOSPage from './pages/SOSPage'
import Dashboard from './pages/Dashboard'
import IncidentDetail from './pages/IncidentDetail'
import Login from './pages/Login'
import UserLogin from './pages/UserLogin'
import AuthChoice from './pages/AuthChoice'
import AuthorityApply from './pages/AuthorityApply'
import UserDashboard from './pages/UserDashboard'
import AuthProvider from './components/AuthProvider'
import ProtectedRoute from './components/ProtectedRoute'
import AuthorityRoute from './components/AuthorityRoute'
import CitizenRoute from './components/CitizenRoute'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path='/' element={<LandingPage />} />
          <Route path='/login' element={<AuthChoice />} />
          <Route path='/login/authority' element={<Login />} />
          <Route path='/login/user' element={<UserLogin />} />
          <Route path='/authority-apply' element={<AuthorityApply />} />
          <Route path='/dashboard' element={<AuthorityRoute><Dashboard /></AuthorityRoute>} />
          <Route path='/me' element={<CitizenRoute><UserDashboard /></CitizenRoute>} />
          <Route path='/incidents/:id' element={<ProtectedRoute><IncidentDetail /></ProtectedRoute>} />
          <Route path='/report' element={<ProtectedRoute><CitizenReportPage /></ProtectedRoute>} />
          <Route path='/sos' element={<SOSPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
