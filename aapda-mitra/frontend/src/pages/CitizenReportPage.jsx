import React, { useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function CitizenReportPage(){
  const [text,setText]=useState('')
  const [locationName, setLocationName] = useState('')
  const [authorityType, setAuthorityType] = useState('FLOOD')
  const [submitting, setSubmitting] = useState(false)

  const AUTHORITY_TYPES = [
    { value: 'FLOOD', label: 'Flood' },
    { value: 'FIRE', label: 'Fire' },
    { value: 'EARTHQUAKE', label: 'Earthquake' },
    { value: 'CYCLONE', label: 'Cyclone' },
    { value: 'LANDSLIDE', label: 'Landslide' },
    { value: 'ROAD_DAMAGE', label: 'Road Damage' },
    { value: 'TREE_FALL', label: 'Fallen Tree' },
    { value: 'ELECTRICITY', label: 'Electricity' },
    { value: 'MEDICAL', label: 'Medical' },
    { value: 'GENERAL', label: 'Other' }
  ]

  const submit=async(e)=>{
    e.preventDefault()
    if (!text.trim()) return
    setSubmitting(true)
    try {
      const selected = (authorityType || 'GENERAL').toUpperCase()
      const body = {
        disaster_type: selected,
        source_type: 'CITIZEN_REPORT',
        raw_text: text,
        location_name: locationName || undefined,
        target_authority_types: selected ? [selected] : []
      }
      await fetch('/incidents',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
      alert('Submitted')
      setText('')
      setLocationName('')
    } finally {
      setSubmitting(false)
    }
  }

  const counter = useMemo(() => text.length, [text])

  return (
    <AppShell
      title="Report a Disaster"
      description="Your report is AI-verified and sent to authorities quickly. Share clear details for best results."
    >
      <div className="report-wrap">
        <div className="report-overline">EMERGENCY REPORT</div>

        <div className="report-steps" aria-hidden="true">
          <div className="report-step report-step-active">
            <div className="report-step-dot">1</div>
            <div className="report-step-label">What Happened</div>
          </div>
          <div className="report-step-line" />
          <div className="report-step">
            <div className="report-step-dot">2</div>
            <div className="report-step-label">Where</div>
          </div>
          <div className="report-step-line" />
          <div className="report-step">
            <div className="report-step-dot">3</div>
            <div className="report-step-label">Evidence</div>
          </div>
        </div>

        <Card variant="glass" className="report-card">
          <form onSubmit={submit} className="report-form">
            <label className="auth-label">Select help category</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {AUTHORITY_TYPES.map(t => {
                const active = authorityType === t.value
                return (
                  <button
                    key={t.value}
                    type="button"
                    className={['ui-pill', active ? 'ui-pill-active' : undefined].filter(Boolean).join(' ')}
                    onClick={() => setAuthorityType(t.value)}
                  >
                    {t.label}
                  </button>
                )
              })}
            </div>

            <label className="auth-label" htmlFor="location">Location (optional)</label>
            <input
              id="location"
              className="ui-input"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
              placeholder="e.g. Sector 12, Noida"
            />

            <label className="auth-label" htmlFor="details">Describe the situation</label>
            <div className="report-textarea-wrap">
              <textarea
                id="details"
                className="ui-input report-textarea"
                value={text}
                onChange={e=>setText(e.target.value)}
                rows={7}
                placeholder="Describe what you see. Be specific about location, water levels, number of people affected..."
              />
              <div className="report-counter">{counter}</div>
            </div>

            <div className="report-actions">
              <Button type="submit" variant="primary" size="lg" loading={submitting} disabled={!text.trim()}>
                Submit Emergency Report
              </Button>
              <div className="report-hint">For immediate danger, use SOS to send your location.</div>
            </div>
          </form>
        </Card>
      </div>
    </AppShell>
  )
}
