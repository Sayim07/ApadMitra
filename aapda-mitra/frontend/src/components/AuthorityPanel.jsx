import React, { useEffect, useState } from 'react'
import { useAuth } from './AuthProvider'

export default function AuthorityPanel({ onClose }){
  const { user, profile } = useAuth()
  const [teams, setTeams] = useState([])
  const [assigning, setAssigning] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [incidentId, setIncidentId] = useState('')
  const [confirm, setConfirm] = useState(false)

  useEffect(()=>{
    const load = async ()=>{
      if (!user) return
      try{
        const token = await user.getIdToken()
        const res = await fetch(`/teams`, { headers: { Authorization: `Bearer ${token}` } })
        const data = await res.json()
        setTeams(data.results || [])
      }catch(e){ console.error(e) }
    }
    load()
  },[user])

  const doAssign = async () => {
    if (!user || !selectedTeam || !incidentId) return alert('Select team and incident ID')
    setAssigning(true)
    try{
      const token = await user.getIdToken()
      const res = await fetch(`/incidents/${incidentId}/assign`, { method: 'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body: JSON.stringify({team_id: selectedTeam.team_id, notes:'Assigned from Authority Panel'}) })
      if (res.ok) {
        alert('Assigned')
        setConfirm(false)
      } else {
        alert('Failed')
      }
    }catch(e){ console.error(e); alert('Error') }
    setAssigning(false)
  }

  return (
    <div style={{position:'fixed', right:20, top:80, width:360, background:'#fff', border:'1px solid #ccc', padding:12, zIndex:2000}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h4>Authority Panel</h4>
        <button onClick={onClose}>Close</button>
      </div>
      <div>
        <p><strong>{profile ? (profile.name || profile.user_id) : 'Authority'}</strong></p>
        <div style={{marginBottom:8}}>
          <label>Incident ID</label>
          <input value={incidentId} onChange={(e)=>setIncidentId(e.target.value)} style={{width:'100%'}} />
        </div>
        <h5>Available Teams</h5>
        {teams.length === 0 && <p>No teams</p>}
        <ul style={{maxHeight:220, overflow:'auto'}}>
          {teams.map(t=> (
            <li key={t.team_id} style={{marginBottom:6}}>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                <div>
                  <div style={{fontWeight:600}}>{t.name}</div>
                  <div style={{fontSize:12, color:'#666'}}>{t.team_id} — {t.district || 'unknown'}</div>
                </div>
                <div>
                  <button onClick={()=>{setSelectedTeam(t); setConfirm(true)}} disabled={assigning}>Assign</button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        {confirm && selectedTeam && (
          <div style={{marginTop:10, padding:8, border:'1px dashed #aaa'}}>
            <div>Assign <strong>{selectedTeam.name}</strong> to incident <strong>{incidentId}</strong>?</div>
            <div style={{marginTop:8, display:'flex', gap:8}}>
              <button onClick={doAssign} disabled={assigning}>Confirm</button>
              <button onClick={()=>{setConfirm(false); setSelectedTeam(null)}}>Cancel</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
