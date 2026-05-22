import React from 'react'
import AppShell from '../components/AppShell'

export default function SOSPage(){
  const sendSOS = async ()=>{
    if(navigator.geolocation){
      navigator.geolocation.getCurrentPosition(async pos=>{
        const body={latitude:pos.coords.latitude, longitude:pos.coords.longitude}
        await fetch('/incidents/sos',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
        alert('SOS Sent')
      }, ()=>alert('Location denied'))
    }else alert('Geolocation not supported')
  }

  return (
    <AppShell
      title="Emergency SOS"
      description="Sends your live location and creates an SOS incident. Use only for urgent situations."
    >
      <div className="grid">
        <div className="col-3" />
        <div className="col-6">
          <div className="card">
            <div className="card-body" style={{ padding: 22, textAlign: 'center' }}>
              <div className="badge badge-red" style={{ justifyContent: 'center', marginBottom: 12 }}>
                <span className="badge-dot" />
                High priority
              </div>
              <h1 style={{ fontSize: 34, marginBottom: 10 }}>Send SOS</h1>
              <p style={{ marginBottom: 18 }}>
                We will request location permissions. If denied, SOS cannot include coordinates.
              </p>
              <button className="btn btn-danger" onClick={sendSOS} style={{ padding: '14px 18px', fontSize: 18 }}>
                Send SOS Now
              </button>
              <div style={{ height: 14 }} />
              <p className="muted-2" style={{ fontSize: 12 }}>
                If you are safe, use “Report” instead for non-urgent updates.
              </p>
            </div>
          </div>
        </div>
        <div className="col-3" />
      </div>
    </AppShell>
  )
}
