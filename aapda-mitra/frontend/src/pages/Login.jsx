import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import AppShell from '../components/AppShell'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      setLoading(true)
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError('Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell
      title="Sign in"
      description="For authorities and responders. Use your Firebase-authenticated account."
    >
      <div className="grid">
        <div className="col-4" />
        <div className="col-4">
          <div className="card">
            <div className="card-body" style={{ padding: 20 }}>
              <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 14 }}>
                <div className="field">
                  <label className="label" htmlFor="email">Email</label>
                  <input
                    id="email"
                    className="input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    autoComplete="email"
                  />
                </div>
                <div className="field">
                  <label className="label" htmlFor="password">Password</label>
                  <input
                    id="password"
                    className="input"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    autoComplete="current-password"
                  />
                </div>
                <button className="btn btn-primary" type="submit" disabled={loading || !email || !password}>
                  {loading ? 'Signing in…' : 'Sign in'}
                </button>
                {error && (
                  <div className="badge badge-red" role="alert" style={{ justifyContent: 'center' }}>
                    <span className="badge-dot" />
                    {error}
                  </div>
                )}
              </form>
            </div>
          </div>
        </div>
        <div className="col-4" />
      </div>
    </AppShell>
  )
}
