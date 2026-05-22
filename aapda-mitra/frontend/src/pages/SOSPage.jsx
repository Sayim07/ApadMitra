import React from 'react'

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
    <div style={{background:'#c0392b',minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',color:'#fff'}}>
      <h1>EMERGENCY SOS</h1>
      <p>Tap to send your location and SOS alert</p>
      <button onClick={sendSOS} style={{padding:20,fontSize:24,borderRadius:8}}>SOS</button>
    </div>
  )
}
