import React from 'react'

const base = 'ui-btn'

const variants = {
  primary: 'ui-btn-primary',
  secondary: 'ui-btn-secondary',
  danger: 'ui-btn-danger',
  ghost: 'ui-btn-ghost',
  outline: 'ui-btn-outline'
}

const sizes = {
  sm: 'ui-btn-sm',
  md: 'ui-btn-md',
  lg: 'ui-btn-lg'
}

export default function Button({
  as: Component = 'button',
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className,
  children,
  ...props
}) {
  const isDisabled = disabled || loading
  return (
    <Component
      className={[base, variants[variant], sizes[size], className].filter(Boolean).join(' ')}
      disabled={Component === 'button' ? isDisabled : undefined}
      aria-disabled={Component !== 'button' ? isDisabled : undefined}
      {...props}
    >
      {loading ? (
        <span className="ui-spinner" aria-label="Loading" />
      ) : (
        children
      )}
    </Component>
  )
}

