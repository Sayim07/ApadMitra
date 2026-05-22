import React, {useState} from 'react'

export default function CitizenReportPage(){
  const [text,setText]=useState('')
  const submit=async(e)=>{
    e.preventDefault()
    const body={disaster_type:'FLOOD', source_type:'CITIZEN_REPORT', raw_text:text}
    await fetch('/incidents',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
    alert('Submitted')
  }
  return (
    <div style={{padding:20}}>
      <h2>Report Emergency</h2>
      <form onSubmit={submit}>
        <textarea value={text} onChange={e=>setText(e.target.value)} rows={6} style={{width:'100%'}} />
        <button type='submit'>Submit</button>
      </form>
    </div>
  )
}
