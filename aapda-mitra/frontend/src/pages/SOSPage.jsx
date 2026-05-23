import React, { useState } from 'react'
import AppShell from '../components/AppShell'
import Button from '../components/ui/Button'

export default function SOSPage(){
  const [status, setStatus] = useState('idle')
  const sendSOS = async ()=>{
    if(navigator.geolocation){
      setStatus('loading')
      navigator.geolocation.getCurrentPosition(async pos=>{
        const body={latitude:pos.coords.latitude, longitude:pos.coords.longitude}
        await fetch('/incidents/sos',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
        alert('SOS Sent')
        setStatus('success')
      }, ()=>{
        alert('Location denied')
        setStatus('error')
      })
    }else {
      alert('Geolocation not supported')
      setStatus('error')
    }
  }

  return (
    <AppShell title="SOS" description="Tap to send your location and alert authorities. Use only for urgent situations.">
      <div className="sos-wrap">
        <div className={['sos-stage', status === 'success' ? 'sos-stage-success' : status === 'error' ? 'sos-stage-error' : undefined].filter(Boolean).join(' ')}>
          {status === 'idle' ? (
            <>
              <div className="sos-rings" aria-hidden="true">
                <div className="sos-ring sos-ring-1" />
                <div className="sos-ring sos-ring-2" />
                <div className="sos-ring sos-ring-3" />
              </div>

              <button className="sos-button" onClick={sendSOS} type="button">
                SOS
              </button>

              <div className="sos-text">Tap to send your location and alert authorities</div>
              <div className="sos-contacts">
                <a className="sos-contact" href="tel:112">📞 112 Emergency</a>
                <a className="sos-contact" href="tel:1077">🌊 1077 Flood</a>
                <a className="sos-contact" href="tel:01124363260">🚁 NDRF: 011-24363260</a>
              </div>
            </>
          ) : null}

          {status === 'loading' ? (
            <>
              <div className="sos-spinner" aria-hidden="true" />
              <div className="sos-title">📍 Getting your location…</div>
              <div className="sos-sub">Please allow location access</div>
            </>
          ) : null}

          {status === 'success' ? (
            <>
              <div className="sos-check" aria-hidden="true">✓</div>
              <div className="sos-title">🆘 SOS Sent</div>
              <div className="sos-sub">Authorities have been alerted. Help is on the way.</div>
              <Button variant="outline" size="md" onClick={() => setStatus('idle')}>Send another</Button>
            </>
          ) : null}

          {status === 'error' ? (
            <>
              <div className="sos-title">We couldn’t get your GPS</div>
              <div className="sos-sub">Please enable location access and try again.</div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
                <Button variant="primary" size="md" onClick={sendSOS}>Try again</Button>
                <Button variant="outline" size="md" onClick={() => setStatus('idle')}>Back</Button>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </AppShell>
  )
}
