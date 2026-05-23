import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import AppShell from '../components/AppShell'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function IncidentDetail(){
  const { id } = useParams()
  const [incident, setIncident] = useState(null)
  const [actions, setActions] = useState([])
  const [loadingAction, setLoadingAction] = useState(false)
  const [showRaw, setShowRaw] = useState(false)
  const { user, profile } = useAuth()

  useEffect(()=>{
    fetch(`/incidents/${id}`).then(r=>r.json()).then(d=>setIncident(d)).catch(()=>setIncident(null))
    // load actions
    (async ()=>{
      try{
        const res = await fetch(`/incidents/${id}/actions`)
        const data = await res.json()
        setActions(data.results || [])
      }catch(e){ console.error(e) }
    })()
  },[id])

  if(!incident) {
    return (
      <AppShell title="Incident" description="Loading incident details…">
        <Card variant="elevated" className="ui-card-pad">Loading…</Card>
      </AppShell>
    )
  }

  const severityVariant = (severity) => {
    const s = (severity || '').toUpperCase()
    if (s === 'RED') return 'red'
    if (s === 'YELLOW') return 'yellow'
    return 'green'
  }

  const callProtected = async (path, method='POST', body=null) => {
    if (!user) { alert('Not authenticated'); return null }
    setLoadingAction(true)
    try {
      const token = await user.getIdToken()
      const res = await fetch(path, {
        method,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: body ? JSON.stringify(body) : undefined
      })
      const data = await res.json()
      return data
    } catch (e) {
      console.error(e)
      return null
    } finally { setLoadingAction(false) }
  }

  const acknowledge = async () => {
    const who = profile ? (profile.user_id || profile.name) : 'authority'
    const r = await callProtected(`/incidents/${id}/acknowledge`, 'PUT', { acknowledged_by: who })
    if (r) { alert('Acknowledged'); setIncident({...incident, acknowledged: true}) }
  }

  const assign = async () => {
    const teamId = prompt('Team id to assign (freeform)')
    if (!teamId) return
    const r = await callProtected(`/incidents/${id}/assign`, 'POST', { team_id: teamId, notes: 'Assigned via authority UI' })
    if (r) { alert('Assigned'); setIncident({...incident, assigned_to: {team_id: teamId}}) }
  }

  const dispatchNow = async () => {
    if (!confirm('Trigger dispatch for this incident now?')) return
    const r = await callProtected(`/incidents/${id}/dispatch`, 'POST')
    if (r && r.ok) { alert('Dispatch triggered'); }
  }

  return (
    <AppShell
      title={`${incident.disaster_type || 'Incident'} — ${incident.location_name || 'Unknown location'}`}
      description={incident.raw_text || 'No description available.'}
      actions={
        <>
          <Button as={Link} to="/dashboard" variant="ghost" size="sm">← Back</Button>
          <Badge variant={severityVariant(incident.severity)} pulse={(incident.severity || '').toUpperCase() === 'RED' && !incident.acknowledged}>
            {(incident.severity || 'GREEN').toUpperCase()}
          </Badge>
        </>
      }
    >
      <div className="grid">
        <section className="col-8">
          <Card variant="elevated">
            <div className="dash-card-head">
              <div>
                <div className="dash-card-title">Incident Details</div>
                <div className="dash-card-subtitle">Verification, location, and status summary</div>
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowRaw(v => !v)}>
                {showRaw ? 'Hide raw JSON' : 'Show raw JSON'}
              </Button>
            </div>
            <div className="dash-card-body">
              <table className="table">
                <tbody>
                  <tr>
                    <td>Severity</td>
                    <td>
                      <Badge variant={severityVariant(incident.severity)} pulse={(incident.severity || '').toUpperCase() === 'RED' && !incident.acknowledged}>
                        {(incident.severity || 'GREEN').toUpperCase()}
                      </Badge>
                    </td>
                  </tr>
                  <tr>
                    <td>Verification</td>
                    <td>
                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                        {(incident.verification_status || 'unknown').toString()}
                      </span>
                      <span style={{ marginLeft: 8, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                        score {incident.verification_score ?? '—'}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td>Location</td>
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{incident.location_name || '—'}</div>
                      <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                        {incident.latitude || incident.lat ? `Lat ${incident.latitude || incident.lat}` : 'Lat —'} ·{' '}
                        {incident.longitude || incident.lng ? `Lng ${incident.longitude || incident.lng}` : 'Lng —'}
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>Status</td>
                    <td>
                      <span style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                        {incident.acknowledged ? 'Acknowledged' : 'Not acknowledged'}
                      </span>
                      {incident.assigned_to?.team_id && (
                        <span style={{ marginLeft: 8, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          assigned to {incident.assigned_to.team_id}
                        </span>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
              {showRaw && (
                <pre style={{ margin: '14px 0 0 0', padding: 12, borderRadius: 12, border: '1px solid var(--border)', background: 'rgba(13,17,23,0.85)', color: 'var(--text-primary)', overflow: 'auto', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                  {JSON.stringify(incident, null, 2)}
                </pre>
              )}
            </div>
          </Card>

          <div style={{ height: 16 }} />

          <Card variant="elevated">
            <div className="dash-card-head">
              <div>
                <div className="dash-card-title">Action History</div>
                <div className="dash-card-subtitle">Recent updates and system actions</div>
              </div>
              <Badge variant="grey">{actions.length} entries</Badge>
            </div>
            <div className="dash-card-body" style={{ display: 'grid', gap: 10 }}>
              {actions.length === 0 && (
                <Badge variant="grey">No actions recorded</Badge>
              )}
              {actions.map((a, i) => (
                <Card key={i} variant="bordered" className="ui-card-pad">
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
                      <div style={{ display: 'grid', gap: 2 }}>
                        <div style={{ fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-display)' }}>{a.action || 'action'}</div>
                        <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          by {a.by || 'system'} · {a.ts ? new Date(a.ts).toLocaleString() : 'unknown time'}
                        </div>
                      </div>
                      {a.provider && (
                        <Badge variant="blue">{a.provider}</Badge>
                      )}
                    </div>
                    {a.details && (
                      <pre style={{ margin: 0, padding: 10, borderRadius: 12, border: '1px solid rgba(255,255,255,0.10)', background: 'rgba(13,17,23,0.85)', color: 'var(--text-primary)', overflow: 'auto', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                        {JSON.stringify(a.details, null, 2)}
                      </pre>
                    )}
                </Card>
              ))}
            </div>
          </Card>
        </section>

        <aside className="col-4">
          {profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') && (
            <Card variant="elevated">
              <div className="dash-card-head">
                <div>
                  <div className="dash-card-title">Authority Actions</div>
                  <div className="dash-card-subtitle">Acknowledge, assign and dispatch</div>
                </div>
                <Badge variant="grey">Protected</Badge>
              </div>
              <div className="dash-card-body" style={{ display: 'grid', gap: 10 }}>
                <Button variant="primary" size="md" onClick={acknowledge} disabled={loadingAction || incident.acknowledged} loading={loadingAction && !incident.acknowledged}>
                  {incident.acknowledged ? 'Acknowledged' : 'Acknowledge'}
                </Button>
                <Button variant="secondary" size="md" onClick={assign} disabled={loadingAction}>
                  Assign team
                </Button>
                <Button variant="danger" size="md" onClick={dispatchNow} disabled={loadingAction}>
                  Dispatch now
                </Button>
                <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                  Actions require a valid auth token.
                </div>
              </div>
            </Card>
          )}

          {!profile && (
            <Card variant="elevated" className="ui-card-pad">
              <div style={{ display: 'grid', gap: 10 }}>
                <div style={{ color: 'var(--text-secondary)' }}>Sign in to access protected authority actions.</div>
                <Button as={Link} to="/login" variant="primary" size="md">Sign in</Button>
              </div>
            </Card>
          )}
        </aside>
      </div>
    </AppShell>
  )
}
