import React from 'react'

export default function Input({
  as: Component = 'input',
  leftIcon,
  rightIcon,
  error,
  className,
  ...props
}) {
  const control = (
    <Component className={['ui-input', leftIcon ? 'ui-input-has-left' : undefined, rightIcon ? 'ui-input-has-right' : undefined, className].filter(Boolean).join(' ')} {...props} />
  )

  return (
    <div className="ui-field">
      <div className="ui-input-wrap">
        {leftIcon ? <span className="ui-input-icon ui-input-icon-left" aria-hidden="true">{leftIcon}</span> : null}
        {control}
        {rightIcon ? <span className="ui-input-icon ui-input-icon-right">{rightIcon}</span> : null}
      </div>
      {error ? <div className="ui-field-error">{error}</div> : null}
    </div>
  )
}

