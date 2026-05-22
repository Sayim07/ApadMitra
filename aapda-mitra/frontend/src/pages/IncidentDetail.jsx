import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import AppShell from '../components/AppShell'

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
        <div className="card">
          <div className="card-body">Loading…</div>
        </div>
      </AppShell>
    )
  }

  const severityBadge = (severity) => {
    const s = (severity || '').toUpperCase()
    if (s === 'RED') return 'badge badge-red'
    if (s === 'YELLOW') return 'badge badge-yellow'
    return 'badge badge-green'
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
          <Link className="btn btn-ghost" to="/dashboard">Back</Link>
          <span className={severityBadge(incident.severity)}>
            <span className="badge-dot" />
            {(incident.severity || 'GREEN').toUpperCase()}
          </span>
        </>
      }
    >
      <div className="grid">
        <section className="col-8">
          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Details</h3>
              <button className="btn btn-ghost" onClick={() => setShowRaw(v => !v)}>
                {showRaw ? 'Hide raw JSON' : 'Show raw JSON'}
              </button>
            </div>
            <div className="card-body">
              <table className="table">
                <tbody>
                  <tr>
                    <td>Severity</td>
                    <td>
                      <span className={severityBadge(incident.severity)}>
                        <span className="badge-dot" />
                        {(incident.severity || 'GREEN').toUpperCase()}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td>Verification</td>
                    <td>
                      <span style={{ fontWeight: 700, color: 'var(--text)' }}>
                        {(incident.verification_status || 'unknown').toString()}
                      </span>
                      <span className="muted-2" style={{ marginLeft: 8, fontSize: 12 }}>
                        score {incident.verification_score ?? '—'}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td>Location</td>
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--text)' }}>{incident.location_name || '—'}</div>
                      <div className="muted-2" style={{ fontSize: 12 }}>
                        {incident.latitude || incident.lat ? `Lat ${incident.latitude || incident.lat}` : 'Lat —'} ·{' '}
                        {incident.longitude || incident.lng ? `Lng ${incident.longitude || incident.lng}` : 'Lng —'}
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>Status</td>
                    <td>
                      <span className="muted">{incident.acknowledged ? 'Acknowledged' : 'Not acknowledged'}</span>
                      {incident.assigned_to?.team_id && (
                        <span className="muted-2" style={{ marginLeft: 8, fontSize: 12 }}>
                          assigned to {incident.assigned_to.team_id}
                        </span>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
              {showRaw && (
                <pre style={{ margin: '14px 0 0 0', padding: 12, borderRadius: 12, border: '1px solid var(--border)', background: 'rgba(10,16,30,0.6)', color: 'var(--text)', overflow: 'auto' }}>
                  {JSON.stringify(incident, null, 2)}
                </pre>
              )}
            </div>
          </div>

          <div style={{ height: 16 }} />

          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Action History</h3>
              <span className="muted-2" style={{ fontSize: 12 }}>{actions.length} entries</span>
            </div>
            <div className="card-body" style={{ display: 'grid', gap: 10 }}>
              {actions.length === 0 && (
                <div className="badge" style={{ justifyContent: 'center' }}>
                  <span className="badge-dot" />
                  No actions recorded
                </div>
              )}
              {actions.map((a, i) => (
                <div key={i} className="card" style={{ boxShadow: 'none' }}>
                  <div className="card-body" style={{ padding: 12, display: 'grid', gap: 8 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
                      <div style={{ display: 'grid', gap: 2 }}>
                        <div style={{ fontWeight: 800, color: 'var(--text)' }}>{a.action || 'action'}</div>
                        <div className="muted-2" style={{ fontSize: 12 }}>
                          by {a.by || 'system'} · {a.ts ? new Date(a.ts).toLocaleString() : 'unknown time'}
                        </div>
                      </div>
                      {a.provider && (
                        <span className="badge">
                          <span className="badge-dot" />
                          {a.provider}
                        </span>
                      )}
                    </div>
                    {a.details && (
                      <pre style={{ margin: 0, padding: 10, borderRadius: 12, border: '1px solid rgba(255,255,255,0.12)', background: 'rgba(10,16,30,0.6)', color: 'var(--text)', overflow: 'auto' }}>
                        {JSON.stringify(a.details, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <aside className="col-4">
          {profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ fontSize: 16 }}>Authority Actions</h3>
                <span className="badge">
                  <span className="badge-dot" />
                  Protected
                </span>
              </div>
              <div className="card-body" style={{ display: 'grid', gap: 10 }}>
                <button className="btn btn-primary" onClick={acknowledge} disabled={loadingAction || incident.acknowledged}>
                  {incident.acknowledged ? 'Acknowledged' : 'Acknowledge'}
                </button>
                <button className="btn" onClick={assign} disabled={loadingAction}>
                  Assign team
                </button>
                <button className="btn btn-danger" onClick={dispatchNow} disabled={loadingAction}>
                  Dispatch now
                </button>
                <p className="muted-2" style={{ fontSize: 12 }}>
                  Actions require a valid auth token. Updates may take a moment to reflect.
                </p>
              </div>
            </div>
          )}

          {!profile && (
            <div className="card">
              <div className="card-body">
                <p>Sign in to view protected actions for this incident.</p>
                <div style={{ height: 12 }} />
                <Link className="btn btn-primary" to="/login">Sign in</Link>
              </div>
            </div>
          )}
        </aside>
      </div>
    </AppShell>
  )
}
