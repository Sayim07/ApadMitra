import React, { useEffect, useState } from 'react'
import { useAuth } from './AuthProvider'

export default function AuthorityPanel({ onClose }){
  const { user, profile } = useAuth()
  const [teams, setTeams] = useState([])
  const [assigning, setAssigning] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [incidentId, setIncidentId] = useState('')
  const [confirm, setConfirm] = useState(false)
  const [error, setError] = useState(null)

  useEffect(()=>{
    const load = async ()=>{
      if (!user) return
      try{
        const token = await user.getIdToken()
        const res = await fetch(`/teams`, { headers: { Authorization: `Bearer ${token}` } })
        const data = await res.json()
        setTeams(data.results || [])
        setError(null)
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
        setSelectedTeam(null)
        setIncidentId('')
        setError(null)
      } else {
        setError('Assignment failed. Please verify the incident ID and try again.')
      }
    }catch(e){ console.error(e); alert('Error') }
    setAssigning(false)
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="card modal">
        <div className="card-header">
          <div style={{ display: 'grid', gap: 4 }}>
            <h3 style={{ fontSize: 16 }}>Authority Panel</h3>
            <span className="muted-2" style={{ fontSize: 12 }}>
              {profile ? (profile.name || profile.user_id) : 'Authority'}
            </span>
          </div>
          <button className="btn btn-ghost" onClick={onClose}>Close</button>
        </div>

        <div className="card-body" style={{ display: 'grid', gap: 12 }}>
          <div className="field">
            <label className="label" htmlFor="incidentId">Incident ID</label>
            <input id="incidentId" className="input" value={incidentId} onChange={(e)=>setIncidentId(e.target.value)} placeholder="Paste incident id" />
          </div>

          {error && (
            <div className="badge badge-red" role="alert" style={{ justifyContent: 'center' }}>
              <span className="badge-dot" />
              {error}
            </div>
          )}

          <div className="divider" />

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
            <h4 style={{ fontSize: 14, margin: 0 }}>Available Teams</h4>
            <span className="muted-2" style={{ fontSize: 12 }}>{teams.length} teams</span>
          </div>

          {teams.length === 0 && (
            <div className="badge" style={{ justifyContent: 'center' }}>
              <span className="badge-dot" />
              No teams available
            </div>
          )}

          <div style={{ maxHeight: 340, overflow: 'auto', display: 'grid', gap: 10 }}>
            {teams.map(t => (
              <div key={t.team_id} className="card" style={{ boxShadow: 'none' }}>
                <div className="card-body" style={{ padding: 12, display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                  <div style={{ display: 'grid', gap: 2 }}>
                    <div style={{ fontWeight: 800, color: 'var(--text)' }}>{t.name || 'Team'}</div>
                    <div className="muted-2" style={{ fontSize: 12 }}>{t.team_id} · {t.district || 'unknown district'}</div>
                  </div>
                  <button
                    className="btn"
                    onClick={() => { setSelectedTeam(t); setConfirm(true); setError(null) }}
                    disabled={assigning}
                  >
                    Assign
                  </button>
                </div>
              </div>
            ))}
          </div>

          {confirm && selectedTeam && (
            <div className="card" style={{ boxShadow: 'none' }}>
              <div className="card-body" style={{ padding: 12, display: 'grid', gap: 10 }}>
                <div>
                  Assign <span style={{ fontWeight: 800, color: 'var(--text)' }}>{selectedTeam.name}</span> to incident{' '}
                  <span style={{ fontWeight: 800, color: 'var(--text)' }}>{incidentId || '—'}</span>?
                </div>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                  <button className="btn btn-primary" onClick={doAssign} disabled={assigning || !incidentId}>
                    {assigning ? 'Assigning…' : 'Confirm'}
                  </button>
                  <button className="btn btn-ghost" onClick={() => { setConfirm(false); setSelectedTeam(null); setError(null) }}>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
