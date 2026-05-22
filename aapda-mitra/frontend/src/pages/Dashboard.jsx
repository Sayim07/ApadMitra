import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DisasterMap from '../components/DisasterMap'
import { useAuth } from '../components/AuthProvider'
import AuthorityPanel from '../components/AuthorityPanel'
import AppShell from '../components/AppShell'

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const { profile } = useAuth()

  useEffect(() => {
    fetch('/incidents/active').then(r => r.json()).then(d => setIncidents(d || [])).catch(() => setIncidents([]))
  }, [])

  const [showPanel, setShowPanel] = useState(false)

  const severityBadge = (severity) => {
    if (severity === 'RED') return 'badge badge-red'
    if (severity === 'YELLOW') return 'badge badge-yellow'
    return 'badge badge-green'
  }

  const countBy = (sev) => incidents.filter(i => (i.severity || '').toUpperCase() === sev).length

  return (
    <AppShell
      title="Active Incidents"
      description="Live incident overview with map, severity breakdown, and quick access to incident details."
      actions={
        profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') ? (
          <button className="btn btn-primary" onClick={() => setShowPanel(true)}>
            Authority Panel
          </button>
        ) : null
      }
    >
      <div className="grid">
        <div className="col-4">
          <div className="kpi">
            <div className="kpi-value">{incidents.length}</div>
            <div className="kpi-label">Active incidents</div>
          </div>
        </div>
        <div className="col-4">
          <div className="kpi">
            <div className="kpi-value" style={{ color: 'var(--danger)' }}>{countBy('RED')}</div>
            <div className="kpi-label">High severity (RED)</div>
          </div>
        </div>
        <div className="col-4">
          <div className="kpi">
            <div className="kpi-value" style={{ color: 'var(--warning)' }}>{countBy('YELLOW')}</div>
            <div className="kpi-label">Medium severity (YELLOW)</div>
          </div>
        </div>

        <section className="col-8">
          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Incident Map</h3>
              <span className="badge">
                <span className="badge-dot" />
                Updated recently
              </span>
            </div>
            <div className="card-body">
              <DisasterMap incidents={incidents} />
            </div>
          </div>
        </section>

        <aside className="col-4">
          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Incident List</h3>
              <span className="muted-2" style={{ fontSize: 12 }}>{incidents.length} total</span>
            </div>
            <div className="card-body" style={{ display: 'grid', gap: 10 }}>
              {incidents.length === 0 && (
                <div className="badge" style={{ justifyContent: 'center' }}>
                  <span className="badge-dot" />
                  No active incidents
                </div>
              )}
              {incidents.map((inc, idx) => {
                const incidentId = inc.id || inc._id || inc.document_id || idx
                return (
                  <div key={incidentId} className="card" style={{ boxShadow: 'none' }}>
                    <div className="card-body" style={{ padding: 12, display: 'grid', gap: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start' }}>
                        <div style={{ display: 'grid', gap: 2 }}>
                          <div style={{ fontWeight: 700, color: 'var(--text)' }}>{inc.disaster_type || 'Incident'}</div>
                          <div className="muted-2" style={{ fontSize: 12 }}>
                            {inc.location_name || 'Unknown location'}
                          </div>
                        </div>
                        <span className={severityBadge((inc.severity || 'GREEN').toUpperCase())}>
                          <span className="badge-dot" />
                          {(inc.severity || 'GREEN').toUpperCase()}
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
                        <span className="muted-2" style={{ fontSize: 12 }}>
                          {(inc.verification_status || 'unknown').toString()}
                        </span>
                        <Link className="btn btn-ghost" to={`/incidents/${incidentId}`} style={{ padding: '8px 10px' }}>
                          View
                        </Link>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </aside>
      </div>

      {showPanel && <AuthorityPanel onClose={() => setShowPanel(false)} />}
    </AppShell>
  )
}
