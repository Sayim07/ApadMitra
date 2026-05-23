import React, { useEffect, useMemo, useState } from 'react'
import Card from './Card'

export default function StatCard({ icon, label, value, trend, tone = 'blue', className }) {
  const [displayValue, setDisplayValue] = useState(0)

  const target = useMemo(() => {
    const n = typeof value === 'number' ? value : Number(value)
    return Number.isFinite(n) ? n : 0
  }, [value])

  useEffect(() => {
    let raf = 0
    const start = performance.now()
    const duration = 1200

    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplayValue(Math.round(eased * target))
      if (t < 1) raf = requestAnimationFrame(tick)
    }

    setDisplayValue(0)
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target])

  const toneClass = tone ? `ui-stat-${tone}` : undefined

  return (
    <Card variant="elevated" className={['ui-stat', toneClass, className].filter(Boolean).join(' ')}>
      <div className="ui-stat-top">
        <div className="ui-stat-icon" aria-hidden="true">{icon}</div>
        {trend ? <div className={['ui-trend', trend.direction === 'up' ? 'ui-trend-up' : 'ui-trend-down'].join(' ')}>{trend.label}</div> : null}
      </div>
      <div className="ui-stat-label">{label}</div>
      <div className="ui-stat-value">{displayValue}</div>
    </Card>
  )
}

