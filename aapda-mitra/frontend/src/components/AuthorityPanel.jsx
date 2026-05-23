import React, { useEffect, useState } from 'react'
import { useAuth } from './AuthProvider'
import Badge from './ui/Badge'
import Button from './ui/Button'
import Card from './ui/Card'
import Input from './ui/Input'

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
      <Card variant="elevated" className="modal">
        <div className="dash-card-head">
          <div style={{ display: 'grid', gap: 4 }}>
            <div className="dash-card-title">Authority Panel</div>
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              {profile ? (profile.name || profile.user_id) : 'Authority'}
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>Close</Button>
        </div>

        <div className="dash-card-body" style={{ display: 'grid', gap: 12 }}>
          <div style={{ display: 'grid', gap: 8 }}>
            <label className="auth-label" htmlFor="incidentId">Incident ID</label>
            <Input id="incidentId" value={incidentId} onChange={(e)=>setIncidentId(e.target.value)} placeholder="Paste incident id" leftIcon="🧾" />
          </div>

          {error && (
            <Badge variant="red" pulse>{error}</Badge>
          )}

          <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800 }}>Available Teams</div>
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{teams.length} teams</div>
          </div>

          {teams.length === 0 && (
            <Badge variant="grey">No teams available</Badge>
          )}

          <div style={{ maxHeight: 340, overflow: 'auto', display: 'grid', gap: 10 }}>
            {teams.map(t => (
              <Card key={t.team_id} variant="bordered" className="ui-card-pad" style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                  <div style={{ display: 'grid', gap: 2 }}>
                    <div style={{ fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-display)' }}>{t.name || 'Team'}</div>
                    <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{t.team_id} · {t.district || 'unknown district'}</div>
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => { setSelectedTeam(t); setConfirm(true); setError(null) }}
                    disabled={assigning}
                  >
                    Assign
                  </Button>
              </Card>
            ))}
          </div>

          {confirm && selectedTeam && (
            <Card variant="glass" className="ui-card-pad" style={{ display: 'grid', gap: 10 }}>
                <div>
                  Assign <span style={{ fontWeight: 800, color: 'var(--text-primary)' }}>{selectedTeam.name}</span> to incident{' '}
                  <span style={{ fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{incidentId || '—'}</span>?
                </div>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                  <Button variant="primary" size="md" onClick={doAssign} disabled={assigning || !incidentId} loading={assigning}>
                    Confirm
                  </Button>
                  <Button variant="ghost" size="md" onClick={() => { setConfirm(false); setSelectedTeam(null); setError(null) }}>
                    Cancel
                  </Button>
                </div>
            </Card>
          )}
        </div>
      </Card>
    </div>
  )
}
