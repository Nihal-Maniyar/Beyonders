import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
  iconRight?: React.ReactNode
  loading?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconRight,
  loading = false,
  disabled,
  className = '',
  ...props
}) => {
  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontFamily: 'var(--font-display)',
    fontWeight: 600,
    borderRadius: 'var(--radius-md)',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled || loading ? 0.6 : 1,
    transition: 'all var(--transition-fast)',
    border: 'none',
    textDecoration: 'none',
  }

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { padding: '6px 12px', fontSize: '0.875rem' },
    md: { padding: '10px 18px', fontSize: '1rem', boxShadow: 'var(--shadow-tactile)' },
    lg: { padding: '14px 24px', fontSize: '1.125rem', boxShadow: '0 4px 0 rgba(0,0,0,0.12)' },
  }

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: 'var(--color-brand)',
      color: '#ffffff',
      borderBottom: '3px solid var(--color-brand-active)',
    },
    secondary: {
      backgroundColor: 'var(--color-surface)',
      color: 'var(--color-text-primary)',
      border: '1px solid var(--color-border)',
      borderBottom: '3px solid var(--color-border-subtle)',
    },
    success: {
      backgroundColor: 'var(--color-success)',
      color: '#ffffff',
      borderBottom: '3px solid var(--color-success-dark)',
    },
    danger: {
      backgroundColor: 'var(--color-misconception)',
      color: '#ffffff',
      borderBottom: '3px solid var(--color-misconception-dark)',
    },
    outline: {
      backgroundColor: 'transparent',
      color: 'var(--color-brand)',
      border: '2px solid var(--color-brand)',
    },
    ghost: {
      backgroundColor: 'transparent',
      color: 'var(--color-text-secondary)',
    },
  }

  return (
    <button
      style={{
        ...baseStyles,
        ...sizeStyles[size],
        ...variantStyles[variant],
      }}
      disabled={disabled || loading}
      className={`btn-tactile ${className}`}
      {...props}
    >
      {loading ? (
        <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>
      ) : (
        icon
      )}
      <span>{children}</span>
      {!loading && iconRight}
    </button>
  )
}
