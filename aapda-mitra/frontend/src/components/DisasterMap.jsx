import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

function HeatmapLayer({ incidents = [] }) {
  const map = useMap()
  
  useEffect(() => {
    if (incidents.length === 0) return
    
    const heat = L.heatLayer(
      incidents.map(inc => [
        inc.latitude || inc.lat,
        inc.longitude || inc.lng,
        (inc.severity === 'RED' ? 0.8 : inc.severity === 'YELLOW' ? 0.5 : 0.2)
      ]),
      { radius: 25, blur: 15, maxZoom: 17 }
    )
    heat.addTo(map)
    return () => map.removeLayer(heat)
  }, [incidents, map])
  
  return null
}

export default function DisasterMap({ incidents = [] }){
  const [showHeatmap, setShowHeatmap] = useState(false)
  const center = incidents.length ? [incidents[0].latitude || incidents[0].lat, incidents[0].longitude || incidents[0].lng] : [20.5937,78.9629]
  
  const markerColor = (severity) => {
    if (severity === 'RED') return '#dc2626'
    if (severity === 'YELLOW') return '#eab308'
    return '#22c55e'
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginBottom: 10 }}>
        <label className="badge" style={{ cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(e) => setShowHeatmap(e.target.checked)}
            style={{ accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          Show heatmap
        </label>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="badge badge-red"><span className="badge-dot" />RED</span>
          <span className="badge badge-yellow"><span className="badge-dot" />YELLOW</span>
          <span className="badge badge-green"><span className="badge-dot" />GREEN</span>
          <span className="muted-2" style={{ fontSize: 12 }}>{incidents.length} incidents</span>
        </div>
      </div>
      <div style={{ height: 420, width: '100%', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.14)' }}>
        <MapContainer center={center} zoom={5} style={{height: '100%', width: '100%'}}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {showHeatmap && <HeatmapLayer incidents={incidents} />}
          {incidents.map((inc, idx) => (
            <Marker 
              key={idx} 
              position={[inc.latitude || inc.lat, inc.longitude || inc.lng]}
              icon={L.icon({
                iconUrl: `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${encodeURIComponent(markerColor(inc.severity))}"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
              })}
            >
              <Popup>
                <div>
                  <strong>{inc.disaster_type}</strong><br/>
                  {inc.location_name}<br/>
                  Severity: <span style={{color: markerColor(inc.severity), fontWeight: 'bold'}}>{inc.severity}</span>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
