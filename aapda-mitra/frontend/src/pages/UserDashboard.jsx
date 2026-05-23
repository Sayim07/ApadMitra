import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import { useAuth } from '../components/AuthProvider'

export default function UserDashboard() {
  const { profile } = useAuth()
  const navigate = useNavigate()
  const [incidentId, setIncidentId] = useState('')

  const goIncident = () => {
    const id = String(incidentId || '').trim()
    if (!id) return
    navigate(`/incidents/${encodeURIComponent(id)}`)
  }

  return (
    <AppShell
      title="My Dashboard"
      description="Your emergency tools — reporting, SOS, and tracking updates."
      actions={
        <Badge variant="red" pulse>🔴 Live Monitoring</Badge>
      }
    >
      <div className="ui-grid">
        <div className="ui-col-6">
          <Card variant="elevated" className="ui-card-pad">
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18 }}>Quick Actions</div>
            <div style={{ height: 10 }} />
            <div style={{ display: 'grid', gap: 10 }}>
              <Button variant="primary" size="lg" onClick={() => navigate('/report')}>🚨 Report Emergency</Button>
              <Button variant="outline" size="lg" onClick={() => navigate('/sos')}>🆘 SOS</Button>
            </div>
          </Card>
        </div>

        <div className="ui-col-6">
          <Card variant="elevated" className="ui-card-pad">
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18 }}>Track an Incident</div>
            <div style={{ height: 10 }} />
            <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
              If you have an incident ID (shared by responders), you can open the incident timeline here.
            </div>
            <div style={{ height: 12 }} />
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: 220 }}>
                <Input value={incidentId} onChange={(e) => setIncidentId(e.target.value)} placeholder="Incident ID" leftIcon="🔎" />
              </div>
              <Button variant="primary" size="md" onClick={goIncident} disabled={!String(incidentId || '').trim()}>
                Open
              </Button>
            </div>
          </Card>
        </div>

        <div className="ui-col-12">
          <Card variant="glass" className="ui-card-pad">
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ display: 'grid', gap: 6 }}>
                <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18 }}>Account</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Signed in as a citizen user.</div>
              </div>
              <Badge variant="green">{profile?.role || 'CITIZEN'}</Badge>
            </div>
            <div style={{ height: 10 }} />
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
              User: {(profile?.name || profile?.user_id || 'Unknown').toString()}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}
