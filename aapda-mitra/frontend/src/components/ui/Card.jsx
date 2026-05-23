import React from 'react'

const base = 'ui-card'

const variants = {
  default: 'ui-card-default',
  elevated: 'ui-card-elevated',
  bordered: 'ui-card-bordered',
  glass: 'ui-card-glass'
}

export default function Card({ as: Component = 'div', variant = 'default', className, children, ...props }) {
  return (
    <Component className={[base, variants[variant], className].filter(Boolean).join(' ')} {...props}>
      {children}
    </Component>
  )
}

