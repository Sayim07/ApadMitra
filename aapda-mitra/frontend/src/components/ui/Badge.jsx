import React from 'react'

const base = 'ui-badge'

const variants = {
  red: 'ui-badge-red',
  yellow: 'ui-badge-yellow',
  green: 'ui-badge-green',
  blue: 'ui-badge-blue',
  grey: 'ui-badge-grey'
}

const sizes = {
  sm: 'ui-badge-sm',
  md: 'ui-badge-md'
}

export default function Badge({ variant = 'grey', size = 'md', pulse = false, className, children, ...props }) {
  return (
    <span
      className={[base, variants[variant], sizes[size], pulse ? 'ui-badge-pulse' : undefined, className]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {children}
    </span>
  )
}

