import React, { useEffect, useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import { useAuth } from '../components/AuthProvider'
import { Link } from 'react-router-dom'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'

const AUTHORITY_TYPES = [
  { value: 'FLOOD', label: 'Flood' },
  { value: 'FIRE', label: 'Fire' },
  { value: 'EARTHQUAKE', label: 'Earthquake' },
  { value: 'CYCLONE', label: 'Cyclone' },
  { value: 'LANDSLIDE', label: 'Landslide' },
  { value: 'ROAD_DAMAGE', label: 'Road Damage' },
  { value: 'TREE_FALL', label: 'Fallen Tree' },
  { value: 'ELECTRICITY', label: 'Electricity' },
  { value: 'MEDICAL', label: 'Medical' },
  { value: 'GENERAL', label: 'General' }
]

const ROLES = [
  { value: 'WARD_OFFICER', label: 'Ward Officer' },
  { value: 'RESCUE_TEAM', label: 'Rescue Team' },
  { value: 'DISTRICT_AUTHORITY', label: 'District Authority' }
]

export default function AuthorityApply() {
  const { user, profile, loginWithGoogle } = useAuth()
  const [name, setName] = useState(profile?.name || '')
  const [phone, setPhone] = useState(profile?.phone || '')
  const [district, setDistrict] = useState(profile?.preferences?.district || '')
  const [requestedRole, setRequestedRole] = useState(profile?.role === 'CITIZEN' ? 'DISTRICT_AUTHORITY' : (profile?.role || 'DISTRICT_AUTHORITY'))
  const [authorityTypes, setAuthorityTypes] = useState(() => {
    const existing = profile?.preferences?.authority_types || []
    return Array.isArray(existing) ? existing : []
  })
  const [submitting, setSubmitting] = useState(false)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setName(profile?.name || '')
    setPhone(profile?.phone || '')
    setDistrict(profile?.preferences?.district || '')
    setRequestedRole(profile?.role === 'CITIZEN' ? 'DISTRICT_AUTHORITY' : (profile?.role || 'DISTRICT_AUTHORITY'))
    const existing = profile?.preferences?.authority_types || []
    setAuthorityTypes(Array.isArray(existing) ? existing : [])
  }, [profile])

  const selectedSet = useMemo(() => new Set((authorityTypes || []).map(v => String(v).toUpperCase())), [authorityTypes])

  const toggleType = (t) => {
    const v = String(t).toUpperCase()
    const next = new Set(selectedSet)
    if (next.has(v)) next.delete(v)
    else next.add(v)
    setAuthorityTypes(Array.from(next))
  }

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setStatus(null)
    if (!user) {
      setError('Please sign in first.')
      return
    }

    setSubmitting(true)
    try {
      const token = await user.getIdToken()
      const res = await fetch('/authority/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          name,
          phone,
          district,
          requested_role: requestedRole,
          authority_types: authorityTypes
        })
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to submit authority request')
      }
      setStatus('submitted')
    } catch (e2) {
      setError(e2?.message || 'Something went wrong')
    } finally {
      setSubmitting(false)
    }
  }

  const handleGoogle = async () => {
    try {
      setError(null)
      setSubmitting(true)
      await loginWithGoogle()
    } catch (e2) {
      const msg = e2?.code ? String(e2.code).replace('auth/', '') : (e2?.message || 'Google sign-in failed')
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AppShell
      title="Authority Registration"
      description="Apply to become an authority responder. The AI Super Admin validates and routes reports based on your selected authority types."
    >
      <div style={{ maxWidth: 860, margin: '0 auto' }}>
        <Card variant="elevated" className="ui-card-pad">
          {!user ? (
            <div style={{ display: 'grid', gap: 12 }}>
              <Badge variant="yellow">Sign in required</Badge>
              {error ? <Badge variant="red" pulse>{error}</Badge> : null}
              <Button type="button" variant="outline" size="lg" onClick={handleGoogle} loading={submitting}>
                Continue with Google
              </Button>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                <Link to="/login/authority" className="auth-link">Sign in as Authority</Link>
                <Link to="/login/user" className="auth-link">Sign in as User</Link>
              </div>
            </div>
          ) : (
          <form onSubmit={submit} style={{ display: 'grid', gap: 14 }}>
            {status === 'submitted' ? (
              <Badge variant="green">✅ Application submitted. Your profile will be upgraded automatically.</Badge>
            ) : null}
            {error ? <Badge variant="red" pulse>{error}</Badge> : null}

            <div className="ui-grid">
              <div className="ui-col-6">
                <div style={{ display: 'grid', gap: 8 }}>
                  <label className="auth-label" htmlFor="name">Name</label>
                  <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" leftIcon="👤" />
                </div>
              </div>
              <div className="ui-col-6">
                <div style={{ display: 'grid', gap: 8 }}>
                  <label className="auth-label" htmlFor="phone">Phone</label>
                  <Input id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91..." leftIcon="📞" />
                </div>
              </div>
            </div>

            <div className="ui-grid">
              <div className="ui-col-6">
                <div style={{ display: 'grid', gap: 8 }}>
                  <label className="auth-label" htmlFor="district">District</label>
                  <Input id="district" value={district} onChange={(e) => setDistrict(e.target.value)} placeholder="e.g. Noida" leftIcon="📍" />
                </div>
              </div>
              <div className="ui-col-6">
                <div style={{ display: 'grid', gap: 8 }}>
                  <label className="auth-label" htmlFor="role">Authority Role</label>
                  <select id="role" className="ui-input" value={requestedRole} onChange={(e) => setRequestedRole(e.target.value)}>
                    {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                  </select>
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gap: 8 }}>
              <label className="auth-label">Authority Types</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                {AUTHORITY_TYPES.map(t => {
                  const active = selectedSet.has(t.value)
                  return (
                    <button
                      key={t.value}
                      type="button"
                      className={['ui-pill', active ? 'ui-pill-active' : undefined].filter(Boolean).join(' ')}
                      onClick={() => toggleType(t.value)}
                    >
                      {t.label}
                    </button>
                  )
                })}
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
                Selected: {(authorityTypes || []).length ? authorityTypes.join(', ') : 'None'}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
              <Button type="submit" variant="primary" size="lg" loading={submitting} disabled={!district || selectedSet.size === 0}>
                Submit Application
              </Button>
            </div>
          </form>
          )}
        </Card>
      </div>
    </AppShell>
  )
}
