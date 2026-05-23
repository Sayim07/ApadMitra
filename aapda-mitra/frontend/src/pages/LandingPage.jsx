import React from 'react'
import { Link } from 'react-router-dom'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'
import Navbar from '../components/ui/Navbar'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'

export default function LandingPage(){
  const { profile, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    if (location.pathname.startsWith('/dashboard')) navigate('/')
  }

  return (
    <div>
      <Navbar profile={profile} onLogout={handleLogout} />

      <section className="ui-hero">
        <div className="ui-hero-inner">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 18 }}>
            <Badge variant="red" pulse>
              🔴 LIVE MONITORING ACTIVE
            </Badge>
          </div>
          <div className="ui-overline">AI-POWERED DISASTER INTELLIGENCE</div>
          <h1 className="ui-hero-title">
            Detect Disasters.
            <br />
            Save <span style={{ color: 'var(--accent-red)' }}>Lives</span>.
          </h1>
          <p className="ui-hero-subtitle">
            AapdaMitra is an autonomous platform that aggregates citizen signals and system inputs to help verify incidents and coordinate response.
          </p>

          <div style={{ height: 22 }} />

          <div className="ui-grid">
            <div className="ui-col-4">
              <StatCard icon="🚨" label="Active Incidents" value={0} tone="red" />
            </div>
            <div className="ui-col-4">
              <StatCard icon="📡" label="Alerts Sent Today" value={0} tone="orange" />
            </div>
            <div className="ui-col-4">
              <StatCard icon="⚡" label="Avg Response (min)" value={0} tone="blue" />
            </div>
          </div>

          <div style={{ height: 22 }} />

          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
            <Button as={Link} to="/report" variant="primary" size="lg">🚨 Report Emergency</Button>
            <Button as={Link} to="/login" variant="outline" size="lg">Authority Login →</Button>
          </div>
        </div>

        <div className="ui-scroll-indicator">
          <div><span>↓</span></div>
        </div>
      </section>

      <div className="ui-container" style={{ paddingTop: 32 }}>
        <section className="ui-section">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: 34, margin: 0 }}>From Tweet to Rescue</h2>
            <p style={{ marginTop: 10 }}>Five steps that move faster than manual workflows.</p>
          </div>

          <div style={{ height: 22 }} />

          <div className="ui-grid">
            {[
              { n: 1, icon: '🛰️', title: 'Monitor', desc: 'Scans sources continuously' },
              { n: 2, icon: '✅', title: 'Verify', desc: 'Cross-checks and scores signals' },
              { n: 3, icon: '🚨', title: 'Prioritize', desc: 'Assigns severity levels quickly' },
              { n: 4, icon: '🌐', title: 'Generate', desc: 'Creates clear alerts and summaries' },
              { n: 5, icon: '📡', title: 'Dispatch', desc: 'Routes information across channels' }
            ].map((s) => (
              <div key={s.n} className="ui-col-4">
                <Card variant="elevated" className="ui-card-pad">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 34, height: 34, borderRadius: 999, display: 'grid', placeItems: 'center', background: 'rgba(230,57,70,0.12)', border: '1px solid rgba(230,57,70,0.25)', fontFamily: 'var(--font-mono)' }}>
                      {s.n}
                    </div>
                    <div style={{ display: 'grid', gap: 2 }}>
                      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>
                        {s.icon} {s.title}
                      </div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{s.desc}</div>
                    </div>
                  </div>
                </Card>
              </div>
            ))}
          </div>
        </section>

        <section className="ui-section">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: 34, margin: 0 }}>Built for Every Disaster</h2>
            <p style={{ marginTop: 10 }}>A consistent interface for multiple emergency types.</p>
          </div>

          <div style={{ height: 22 }} />

          <div className="ui-grid">
            {[
              { icon: '🌊', name: 'Floods', desc: 'Rapid water rise and overflow monitoring' },
              { icon: '🌀', name: 'Cyclones', desc: 'Wind speed, alerts and evacuation support' },
              { icon: '🏔️', name: 'Earthquakes', desc: 'Seismic signals and aftershock tracking' },
              { icon: '⛰️', name: 'Landslides', desc: 'Slope events and blocked route awareness' },
              { icon: '🔥', name: 'Wildfires', desc: 'Hotspot clustering and containment updates' },
              { icon: '⚡', name: 'Any Emergency', desc: 'Citizen-first reporting with rapid triage' }
            ].map((t) => (
              <div key={t.name} className="ui-col-4">
                <Card variant="elevated" className="ui-card-pad">
                  <div style={{ fontSize: 34 }}>{t.icon}</div>
                  <div style={{ height: 8 }} />
                  <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 16 }}>{t.name}</div>
                  <div style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: 13 }}>{t.desc}</div>
                </Card>
              </div>
            ))}
          </div>
        </section>

        <section className="ui-section">
          <Card variant="elevated" className="ui-card-pad" style={{ background: 'linear-gradient(135deg, #1a0608 0%, #0D1117 100%)', borderColor: 'rgba(230,57,70,0.3)' }}>
            <div style={{ textAlign: 'center' }}>
              <h2 style={{ fontSize: 30, margin: 0 }}>Every second you wait is a life at risk.</h2>
              <p style={{ marginTop: 10 }}>Use AapdaMitra to share, verify and coordinate response.</p>
              <div style={{ height: 16 }} />
              <Button as={Link} to="/login" variant="primary" size="lg">Get Started Free</Button>
            </div>
          </Card>
        </section>

        <footer style={{ padding: '26px 0 42px 0' }}>
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 22 }} />
          <div className="ui-grid">
            <div className="ui-col-4">
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18 }}>
                <span style={{ color: 'var(--accent-red)' }}>Aapda</span>Mitra
              </div>
              <p style={{ marginTop: 10 }}>Emergency intelligence for fast, coordinated response.</p>
            </div>
            <div className="ui-col-4">
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>Product</div>
              <div style={{ display: 'grid', gap: 8, marginTop: 10 }}>
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/report">Report</Link>
                <Link to="/sos">SOS</Link>
              </div>
            </div>
            <div className="ui-col-4">
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>Emergency</div>
              <div style={{ display: 'grid', gap: 8, marginTop: 10 }}>
                <a href="tel:112">📞 112 Emergency</a>
                <a href="tel:1077">🌊 1077 Flood</a>
                <a href="tel:01124363260">🚁 NDRF: 011-24363260</a>
              </div>
            </div>
          </div>
          <div style={{ height: 20 }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', color: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            <span>© {new Date().getFullYear()} AapdaMitra</span>
            <span>Built for disaster response</span>
          </div>
        </footer>
      </div>
    </div>
  )
}
