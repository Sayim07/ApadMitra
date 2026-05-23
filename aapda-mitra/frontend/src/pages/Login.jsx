import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
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
    <div className="auth-split">
      <div className="auth-left" aria-hidden="true">
        <div className="auth-left-inner">
          <div className="auth-brand">
            <span className="auth-bolt">⚡</span>
            <span className="auth-brand-text"><span className="auth-brand-accent">Aapda</span>Mitra</span>
          </div>

          <div className="auth-quote">
            “In disaster response, every second counts.
            <br />
            AapdaMitra makes seconds matter.”
          </div>

          <div className="auth-trust">
            <Badge variant="red" pulse>🔴 Live Monitoring Active</Badge>
            <Badge variant="blue">🛡️ AI-Verified Reports</Badge>
            <Badge variant="grey">📡 5-Channel Alerts</Badge>
          </div>

          <div className="auth-stats">
            <div className="auth-stat">127 incidents verified this month</div>
            <div className="auth-stat">&lt; 30 second average response time</div>
            <div className="auth-stat">3 languages, 5 alert channels</div>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-right-inner">
          <Card variant="elevated" className="auth-card">
            <div style={{ display: 'grid', gap: 10 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 28, fontWeight: 800 }}>Welcome back</h2>
                <p style={{ marginTop: 8 }}>Sign in to access the emergency dashboard</p>
              </div>

              <div className="auth-divider">
                <span>— or sign in with email —</span>
              </div>

              <form onSubmit={handleSubmit} className={['auth-form', error ? 'auth-form-error' : undefined].filter(Boolean).join(' ')}>
                <label className="auth-label" htmlFor="email">Email</label>
                <Input
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  autoComplete="email"
                  leftIcon="✉"
                />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
                  <label className="auth-label" htmlFor="password">Password</label>
                  <Link to="/" className="auth-link">Forgot password?</Link>
                </div>
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  leftIcon="🔒"
                  rightIcon={
                    <button
                      type="button"
                      className="auth-eye"
                      onClick={() => setShowPassword(v => !v)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? '🙈' : '👁'}
                    </button>
                  }
                />

                <Button type="submit" variant="primary" size="lg" loading={loading} disabled={!email || !password}>
                  Sign in
                </Button>

                {error ? (
                  <div style={{ marginTop: 10 }}>
                    <Badge variant="red" pulse>{error}</Badge>
                  </div>
                ) : null}

                <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', fontSize: 13 }}>
                  <Link to="/" className="auth-link">← Back to home</Link>
                  <Link to="/report" className="auth-link">Report without login →</Link>
                </div>
              </form>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
