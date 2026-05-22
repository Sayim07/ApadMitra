import React, {useState} from 'react'
import AppShell from '../components/AppShell'

export default function CitizenReportPage(){
  const [text,setText]=useState('')
  const [disasterType, setDisasterType] = useState('FLOOD')
  const [locationName, setLocationName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const submit=async(e)=>{
    e.preventDefault()
    setSubmitting(true)
    try {
      const body = {
        disaster_type: disasterType,
        source_type: 'CITIZEN_REPORT',
        raw_text: text,
        location_name: locationName || undefined
      }
      await fetch('/incidents',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
      alert('Submitted')
      setText('')
      setLocationName('')
    } finally {
      setSubmitting(false)
    }
  }
  return (
    <AppShell
      title="Report an Emergency"
      description="Share what happened and where. This creates a new incident for verification and response."
    >
      <div className="grid">
        <section className="col-8">
          <div className="card">
            <div className="card-body" style={{ padding: 20 }}>
              <form onSubmit={submit} style={{ display: 'grid', gap: 14 }}>
                <div className="grid">
                  <div className="col-6">
                    <div className="field">
                      <label className="label" htmlFor="disasterType">Disaster type</label>
                      <select
                        id="disasterType"
                        className="select"
                        value={disasterType}
                        onChange={(e) => setDisasterType(e.target.value)}
                      >
                        <option value="FLOOD">Flood</option>
                        <option value="FIRE">Fire</option>
                        <option value="EARTHQUAKE">Earthquake</option>
                        <option value="CYCLONE">Cyclone</option>
                        <option value="LANDSLIDE">Landslide</option>
                        <option value="OTHER">Other</option>
                      </select>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="field">
                      <label className="label" htmlFor="locationName">Location (optional)</label>
                      <input
                        id="locationName"
                        className="input"
                        value={locationName}
                        onChange={(e) => setLocationName(e.target.value)}
                        placeholder="e.g. Sector 12, Noida"
                      />
                    </div>
                  </div>
                </div>

                <div className="field">
                  <label className="label" htmlFor="details">What happened?</label>
                  <textarea
                    id="details"
                    className="textarea"
                    value={text}
                    onChange={e=>setText(e.target.value)}
                    placeholder="Describe the situation, approximate location, and any urgent needs."
                  />
                </div>

                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
                  <button className="btn btn-primary" type="submit" disabled={submitting || !text.trim()}>
                    {submitting ? 'Submitting…' : 'Submit Report'}
                  </button>
                  <span className="muted-2" style={{ fontSize: 12 }}>
                    For immediate danger, use SOS to send your live location.
                  </span>
                </div>
              </form>
            </div>
          </div>
        </section>
        <aside className="col-4">
          <div className="card">
            <div className="card-header">
              <h3 style={{ fontSize: 16 }}>Good reports include</h3>
            </div>
            <div className="card-body">
              <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--muted)', lineHeight: 1.6 }}>
                <li>What and where</li>
                <li>Approximate time</li>
                <li>People affected</li>
                <li>Urgent needs (medical, shelter, rescue)</li>
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </AppShell>
  )
}
