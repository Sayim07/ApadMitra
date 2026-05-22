import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider'

export default function IncidentDetail(){
  const { id } = useParams()
  const [incident, setIncident] = useState(null)
  const [actions, setActions] = useState([])
  const [loadingAction, setLoadingAction] = useState(false)
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

  if(!incident) return <div style={{padding:20}}>Loading...</div>

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
    <div style={{padding:20}}>
      <h2>{incident.disaster_type} — {incident.location_name}</h2>
      <p><strong>Severity:</strong> {incident.severity}</p>
      <p><strong>Verification:</strong> {incident.verification_status} ({incident.verification_score})</p>
      <p>{incident.raw_text}</p>
      <pre style={{background:'#f6f6f6', padding:10}}>{JSON.stringify(incident, null, 2)}</pre>

      {profile && (profile.role === 'DISTRICT_AUTHORITY' || profile.role === 'ADMIN') && (
        <div style={{marginTop:20, padding:10, border:'1px solid #ccc'}}>
          <h3>Authority Actions</h3>
          <div style={{display:'flex', gap:10}}>
            <button onClick={acknowledge} disabled={loadingAction || incident.acknowledged}>Acknowledge</button>
            <button onClick={assign} disabled={loadingAction}>Assign</button>
            <button onClick={dispatchNow} disabled={loadingAction}>Dispatch Now</button>
          </div>
        </div>
      )}
      <div style={{marginTop:20}}>
        <h4>Action History</h4>
        {actions.length === 0 && <p>No actions recorded.</p>}
        <ul>
          {actions.map((a, i) => (
            <li key={i} style={{marginBottom:8}}>
              <div><strong>{a.action}</strong> — by {a.by || a.by || 'system'} at {a.ts ? new Date(a.ts).toLocaleString() : 'unknown'}</div>
              {a.details && <pre style={{background:'#f6f6f6', padding:6}}>{JSON.stringify(a.details, null, 2)}</pre>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
