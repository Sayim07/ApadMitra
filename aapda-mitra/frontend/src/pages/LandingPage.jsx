import React from 'react'

export default function LandingPage(){
  return (
    <div style={{background:'#1a1a2e',minHeight:'100vh',color:'#fff',padding:40}}>
      <h1 style={{color:'#e74c3c'}}>AapdaMitra 2.0</h1>
      <p>From Tweet to Rescue in 30 Seconds</p>
      <div style={{marginTop:20}}>
        <a href="/report" style={{marginRight:12}}>Report Emergency</a>
        <a href="/sos">SOS</a>
      </div>
    </div>
  )
}
