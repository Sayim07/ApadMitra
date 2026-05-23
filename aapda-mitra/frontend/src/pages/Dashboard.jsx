import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DisasterMap from '../components/DisasterMap'
import { useAuth } from '../components/AuthProvider'
import AuthorityPanel from '../components/AuthorityPanel'
import AppShell from '../components/AppShell'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const { profile } = useAuth()

  useEffect(() => {
    fetch('/incidents/active').then(r => r.json()).then(d => setIncidents(d || [])).catch(() => setIncidents([]))
  }, [])

  const [showPanel, setShowPanel] = useState(false)

  const countBy = (sev) => incidents.filter(i => (i.severity || '').toUpperCase() === sev).length
  const hasCriticalUnacked = incidents.some(i => (i.severity || '').toUpperCase() === 'RED' && !i.acknowledged)

  const badgeVariant = (severity) => {
    const s = (severity || '').toUpperCase()
    if (s === 'RED') return 'red'
    if (s === 'YELLOW') return 'yellow'
    return 'green'
  }

  return (
    <AppShell
      title="Dashboard"
      description="Emergency intelligence — incidents, severity, and live map in one view."
      actions={
        profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') ? (
          <Button variant="primary" size="md" onClick={() => setShowPanel(true)}>
            Open Authority Panel
          </Button>
        ) : null
      }
    >
      {hasCriticalUnacked ? (
        <div className="dash-alert">
          <div className="dash-alert-inner">
            <div className="dash-alert-text">⚠ CRITICAL ALERT — Unacknowledged RED incidents detected</div>
            <Button as={Link} to="/dashboard" variant="outline" size="sm">View & Acknowledge →</Button>
          </div>
        </div>
      ) : null}

      <div className="dash-shell">
        <aside className="dash-sidebar">
          <div className="dash-sidebar-section">
            <div className="dash-sidebar-title">OVERVIEW</div>
            <a className="dash-nav-item dash-nav-item-active" href="#map">🗺️ Live Map</a>
            <a className="dash-nav-item" href="#incidents">
              🚨 Active Incidents <span className="dash-count">{incidents.length}</span>
            </a>
            <a className="dash-nav-item" href="#stats">📊 Analytics</a>
          </div>
          <div className="dash-sidebar-section">
            <div className="dash-sidebar-title">MANAGEMENT</div>
            <a className="dash-nav-item" href="#history">📋 Alert History</a>
            <a className="dash-nav-item" href="#contacts">👥 Authority Contacts</a>
            <a className="dash-nav-item" href="#settings">⚙️ Settings</a>
          </div>

          <Card variant="glass" className="dash-health">
            <div className="dash-health-title">System Health</div>
            <div className="dash-health-row"><span>API</span><span>✅ Online</span></div>
            <div className="dash-health-row"><span>Firebase</span><span>✅ Connected</span></div>
            <div className="dash-health-row"><span>Agents</span><span>✅ Running</span></div>
          </Card>
        </aside>

        <main className="dash-main">
          <div id="stats" className="ui-grid">
            <div className="ui-col-3">
              <StatCard icon="🔴" label="Active RED" value={countBy('RED')} tone="red" />
            </div>
            <div className="ui-col-3">
              <StatCard icon="🟡" label="Active YELLOW" value={countBy('YELLOW')} tone="orange" />
            </div>
            <div className="ui-col-3">
              <StatCard icon="⚡" label="Total Active" value={incidents.length} tone="blue" />
            </div>
            <div className="ui-col-3">
              <StatCard icon="✅" label="Other" value={Math.max(0, incidents.length - countBy('RED') - countBy('YELLOW'))} tone="green" />
            </div>
          </div>

          <div style={{ height: 16 }} />

          <Card variant="elevated" className="dash-card" id="map">
            <div className="dash-card-head">
              <div>
                <div className="dash-card-title">Live Map</div>
                <div className="dash-card-subtitle">Severity markers and optional heatmap overlay</div>
              </div>
              <Badge variant={hasCriticalUnacked ? 'red' : 'green'} pulse={hasCriticalUnacked}>
                {hasCriticalUnacked ? '⚠ ACTIVE EMERGENCY' : 'MONITORING ACTIVE'}
              </Badge>
            </div>
            <div className="dash-card-body">
              <DisasterMap incidents={incidents} />
            </div>
          </Card>

          <div style={{ height: 16 }} />

          <Card variant="elevated" className="dash-card" id="incidents">
            <div className="dash-card-head">
              <div>
                <div className="dash-card-title">Active Incidents</div>
                <div className="dash-card-subtitle">Select an incident to view details and actions</div>
              </div>
              <Badge variant="grey">{incidents.length} total</Badge>
            </div>
            <div className="dash-card-body">
              <div className="dash-list">
                {incidents.length === 0 ? (
                  <div className="dash-empty">
                    <div className="dash-empty-icon">🛡️</div>
                    <div className="dash-empty-title">No active incidents</div>
                    <div className="dash-empty-sub">Monitoring is running. New incidents will appear here.</div>
                  </div>
                ) : incidents.map((inc, idx) => {
                  const incidentId = inc.id || inc._id || inc.document_id || idx
                  const sev = (inc.severity || 'GREEN').toUpperCase()
                  const pulse = sev === 'RED' && !inc.acknowledged
                  return (
                    <Link key={incidentId} to={`/incidents/${incidentId}`} className={['dash-item', pulse ? 'dash-item-critical' : undefined].filter(Boolean).join(' ')}>
                      <div className={['dash-sev', `dash-sev-${sev.toLowerCase()}`].join(' ')} />
                      <div className="dash-item-main">
                        <div className="dash-item-top">
                          <div className="dash-item-title">{inc.disaster_type || 'Incident'} · {inc.location_name || 'Unknown location'}</div>
                          <Badge variant={badgeVariant(sev)} pulse={pulse}>{sev}</Badge>
                        </div>
                        <div className="dash-item-sub">
                          <span className="dash-mono">{(inc.verification_status || 'unknown').toString()}</span>
                          {inc.acknowledged ? <span className="dash-muted">Acknowledged</span> : <span className="dash-muted">Unacknowledged</span>}
                        </div>
                      </div>
                      <div className="dash-item-cta">View →</div>
                    </Link>
                  )
                })}
              </div>
            </div>
          </Card>
        </main>

        <aside className="dash-feed">
          <div className="dash-feed-head">
            <Badge variant="red" pulse>● Live Feed</Badge>
            <div className="dash-feed-sub">{incidents.length} updates</div>
          </div>
          <div className="dash-feed-body">
            {incidents.slice(0, 12).map((inc, idx) => {
              const sev = (inc.severity || 'GREEN').toUpperCase()
              const incidentId = inc.id || inc._id || inc.document_id || idx
              return (
                <Link key={`${incidentId}-feed`} className="dash-feed-item" to={`/incidents/${incidentId}`}>
                  <div className={['dash-feed-sev', `dash-sev-${sev.toLowerCase()}`].join(' ')} />
                  <div className="dash-feed-main">
                    <div className="dash-feed-title">{inc.disaster_type || 'Incident'} · {inc.location_name || 'Unknown'}</div>
                    <div className="dash-feed-meta">
                      <span className="dash-mono">{sev}</span>
                      <span className="dash-muted">{inc.acknowledged ? 'ack' : 'unack'}</span>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </aside>
      </div>

      {showPanel && <AuthorityPanel onClose={() => setShowPanel(false)} />}
    </AppShell>
  )
}
