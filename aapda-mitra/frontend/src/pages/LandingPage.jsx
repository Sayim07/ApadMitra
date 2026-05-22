import React from 'react'
import { Link } from 'react-router-dom'
import AppShell from '../components/AppShell'

export default function LandingPage(){
  return (
    <AppShell
      title="From signal to response, fast."
      description="AapdaMitra helps communities and authorities coordinate disaster reporting, verification, and response with a live incident dashboard."
      actions={
        <>
          <Link className="btn btn-primary" to="/report">Report Emergency</Link>
          <Link className="btn btn-danger" to="/sos">SOS</Link>
        </>
      }
    >
      <div className="grid">
        <section className="col-8">
          <div className="card">
            <div className="card-body" style={{ padding: 22 }}>
              <h1 style={{ fontSize: 44, lineHeight: 1.05, marginBottom: 12 }}>
                AapdaMitra
              </h1>
              <p style={{ fontSize: 16, maxWidth: 620 }}>
                Report emergencies, view active incidents on the map, and coordinate with response teams. Designed for clarity under pressure.
              </p>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 16 }}>
                <Link className="btn btn-primary" to="/dashboard">Open Dashboard</Link>
                <Link className="btn" to="/login">Authority Sign in</Link>
              </div>
              <div style={{ height: 18 }} />
              <div className="divider" />
              <div style={{ height: 18 }} />
              <div className="grid" style={{ gap: 12 }}>
                <div className="col-6">
                  <div className="kpi">
                    <div className="kpi-value">Live Map</div>
                    <div className="kpi-label">See incidents and severity at a glance</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="kpi">
                    <div className="kpi-value">Fast SOS</div>
                    <div className="kpi-label">One tap location share for emergencies</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="kpi">
                    <div className="kpi-value">Action History</div>
                    <div className="kpi-label">Track acknowledgements and dispatch</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="kpi">
                    <div className="kpi-value">Authority Tools</div>
                    <div className="kpi-label">Assign teams and coordinate response</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside className="col-4">
          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Quick start</h3>
              <span className="badge">
                <span className="badge-dot" />
                Ready
              </span>
            </div>
            <div className="card-body">
              <ol style={{ margin: 0, paddingLeft: 18, color: 'var(--muted)', lineHeight: 1.6 }}>
                <li>Open the dashboard to see active incidents.</li>
                <li>Report an emergency from the citizen form.</li>
                <li>Use SOS to share live location for urgent help.</li>
              </ol>
              <div style={{ height: 14 }} />
              <p className="muted-2" style={{ fontSize: 12 }}>
                Tip: use Authority Sign in to acknowledge, assign, and dispatch.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </AppShell>
  )
}
