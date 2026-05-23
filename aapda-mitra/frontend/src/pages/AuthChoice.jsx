import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export default function AuthChoice() {
  const location = useLocation()
  const from = location.state?.from || null

  return (
    <div className="ui-container" style={{ paddingTop: 110 }}>
      <div style={{ maxWidth: 980, margin: '0 auto', textAlign: 'center' }}>
        <Badge variant="red" pulse>🔴 Live Monitoring Active</Badge>
        <h1 style={{ marginTop: 18, fontSize: 42 }}>Sign in</h1>
        <p style={{ marginTop: 10 }}>Choose how you want to use AapdaMitra.</p>

        <div style={{ height: 18 }} />

        <div className="ui-grid">
          <div className="ui-col-6">
            <Card variant="elevated" className="ui-card-pad" style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>FOR CITIZENS</div>
              <div style={{ height: 10 }} />
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22 }}>User Login</div>
              <p style={{ marginTop: 10 }}>Sign in to track reports, view updates, and receive alerts.</p>
              <div style={{ height: 12 }} />
              <Button as={Link} to="/login/user" state={{ from }} variant="primary" size="lg">Continue as User</Button>
            </Card>
          </div>

          <div className="ui-col-6">
            <Card variant="elevated" className="ui-card-pad" style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>FOR RESPONDERS</div>
              <div style={{ height: 10 }} />
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22 }}>Authority Login</div>
              <p style={{ marginTop: 10 }}>Sign in to access the emergency dashboard and response tools.</p>
              <div style={{ height: 12 }} />
              <Button as={Link} to="/login/authority" state={{ from }} variant="primary" size="lg">Continue as Authority</Button>
              <div style={{ height: 12 }} />
              <Button as={Link} to="/authority-apply" variant="outline" size="md">Authority registration</Button>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
