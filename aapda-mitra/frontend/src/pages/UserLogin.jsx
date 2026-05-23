import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'

export default function UserLogin() {
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { login, register, loginWithGoogle, isFirebaseConfigured } = useAuth()
  const navigate = useNavigate()

  const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v || '').trim())

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      if (!isValidEmail(email)) {
        setError('Please enter a valid email address')
        return
      }
      setLoading(true)
      if (mode === 'signup') {
        const r = await register(email, password)
        const role = r?.profile?.role
        if (role && role !== 'CITIZEN') {
          navigate('/dashboard', { replace: true })
          return
        }
      } else {
        const r = await login(email, password)
        const role = r?.profile?.role
        if (role && role !== 'CITIZEN') {
          navigate('/dashboard', { replace: true })
          return
        }
      }
      navigate('/me', { replace: true })
    } catch (err) {
      const msg = err?.code ? String(err.code).replace('auth/', '') : (err?.message || 'Failed to authenticate')
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogle = async () => {
    try {
      setError(null)
      setLoading(true)
      const r = await loginWithGoogle()
      const role = r?.profile?.role
      if (role && role !== 'CITIZEN') {
        navigate('/dashboard', { replace: true })
        return
      }
      navigate('/me', { replace: true })
    } catch (err) {
      const msg = err?.code ? String(err.code).replace('auth/', '') : (err?.message || 'Google sign-in failed')
      setError(msg)
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
            “Report fast. Get help faster.”
          </div>

          <div className="auth-trust">
            <Badge variant="red" pulse>🔴 Live Monitoring Active</Badge>
            <Badge variant="grey">🧭 Location-based response</Badge>
            <Badge variant="blue">📡 Multi-channel alerts</Badge>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-right-inner">
          <Card variant="elevated" className="auth-card">
            <div style={{ display: 'grid', gap: 10 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 28, fontWeight: 800 }}>{mode === 'signup' ? 'Create account' : 'User sign in'}</h2>
                <p style={{ marginTop: 8 }}>{mode === 'signup' ? 'Create a citizen account to track reports.' : 'Sign in to receive updates and alerts.'}</p>
              </div>

              {!isFirebaseConfigured ? (
                <>
                  <Badge variant="yellow">Firebase auth is not configured for this local preview</Badge>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                    Create `aapda-mitra/frontend/.env` from `.env.example`, fill VITE_FIREBASE_* values, then restart `npm start`.
                  </div>
                  <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                    <Link to="/login" className="auth-link">← Back</Link>
                  </div>
                </>
              ) : (
                <>
                  <div className="auth-divider">
                    <span>— continue —</span>
                  </div>

                  <Button type="button" variant="outline" size="lg" onClick={handleGoogle} loading={loading}>
                    Continue with Google
                  </Button>

                  <div className="auth-divider">
                    <span>— or {mode === 'signup' ? 'sign up' : 'sign in'} with email —</span>
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

                    <label className="auth-label" htmlFor="password">Password</label>
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
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
                      {mode === 'signup' ? 'Create account' : 'Sign in'}
                    </Button>

                    {error ? (
                      <div style={{ marginTop: 10 }}>
                        <Badge variant="red" pulse>{error}</Badge>
                      </div>
                    ) : null}

                    <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', fontSize: 13 }}>
                      <Link to="/login" className="auth-link">← Back</Link>
                      <button type="button" className="auth-link" onClick={() => setMode(m => (m === 'signup' ? 'signin' : 'signup'))}>
                        {mode === 'signup' ? 'Already have an account?' : 'Create account'}
                      </button>
                    </div>
                  </form>
                </>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
