import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DisasterMap from '../components/DisasterMap'
import { useAuth } from '../components/AuthProvider'
import AuthorityPanel from '../components/AuthorityPanel'

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const { profile, logout } = useAuth()

  useEffect(() => {
    fetch('/incidents/active').then(r => r.json()).then(d => setIncidents(d || [])).catch(() => setIncidents([]))
  }, [])

  const [showPanel, setShowPanel] = useState(false)

  return (
    <div style={{padding:20}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h2>Active Incidents</h2>
        <div>
          {profile ? (
            <div>
              <strong>{profile.name || profile.user_id}</strong> ({profile.role}) {' '}
              <button onClick={() => logout()}>Logout</button>
            </div>
          ) : (
            <a href="/login">Sign in</a>
          )}
        </div>
      </div>
      <DisasterMap incidents={incidents} />
      {incidents.length === 0 && <p>No active incidents</p>}
      <ul>
        {incidents.map((inc, idx) => (
          <li key={idx} style={{marginBottom:10}}>
            <strong>{inc.disaster_type}</strong> at {inc.location_name} — <em>{inc.severity}</em>
            {' '}<Link to={`/incidents/${inc.id || inc._id || inc.document_id || idx}`}>View</Link>
          </li>
        ))}
      </ul>

      {profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') && (
        <div style={{marginTop:20, padding:10, border:'1px solid #ccc'}}>
          <h3>Authority Controls</h3>
          <p>As an authority, you can assign incidents, acknowledge, and dispatch resources.</p>
          <button onClick={() => setShowPanel(true)}>Open Authority Panel</button>
        </div>
      )}

      {showPanel && <AuthorityPanel onClose={() => setShowPanel(false)} />}
    </div>
  )
}
