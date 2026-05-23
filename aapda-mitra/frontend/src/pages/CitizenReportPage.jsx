import React, { useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function CitizenReportPage(){
  const [text,setText]=useState('')
  const submit=async(e)=>{
    e.preventDefault()
    const body={disaster_type:'FLOOD', source_type:'CITIZEN_REPORT', raw_text:text}
    await fetch('/incidents',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
    alert('Submitted')
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
              <Button type="submit" variant="primary" size="lg">
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
