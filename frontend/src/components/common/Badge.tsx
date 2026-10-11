import React from 'react'

export interface BadgeProps {
  children: React.ReactNode
  variant?: 'brand' | 'concept' | 'success' | 'misconception' | 'socratic' | 'warning' | 'neutral'
  size?: 'sm' | 'md'
  icon?: React.ReactNode
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  icon,
}) => {
  const styles: Record<string, React.CSSProperties> = {
    brand: {
      backgroundColor: 'var(--color-brand-light)',
      color: 'var(--color-brand)',
      border: '1px solid var(--color-brand-border)',
    },
    concept: {
      backgroundColor: 'var(--color-denominator-bg)',
      color: 'var(--color-denominator)',
      border: '1px solid var(--color-denominator-border)',
    },
    success: {
      backgroundColor: 'var(--color-success-bg)',
      color: 'var(--color-success-dark)',
      border: '1px solid var(--color-success-border)',
    },
    misconception: {
      backgroundColor: 'var(--color-misconception-bg)',
      color: 'var(--color-misconception-dark)',
      border: '1px solid var(--color-misconception-border)',
    },
    socratic: {
      backgroundColor: 'var(--color-socratic-bg)',
      color: 'var(--color-socratic-dark)',
      border: '1px solid var(--color-socratic-border)',
    },
    warning: {
      backgroundColor: 'var(--color-warning-bg)',
      color: 'var(--color-warning)',
      border: '1px solid var(--color-warning-border)',
    },
    neutral: {
      backgroundColor: '#f1f5f9',
      color: '#475569',
      border: '1px solid #e2e8f0',
    },
  }

  const sizeStyle: React.CSSProperties =
    size === 'sm'
      ? { padding: '2px 8px', fontSize: '0.75rem', gap: '4px' }
      : { padding: '4px 10px', fontSize: '0.85rem', gap: '6px' }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        fontFamily: 'var(--font-display)',
        fontWeight: 600,
        borderRadius: 'var(--radius-full)',
        lineHeight: 1.2,
        ...sizeStyle,
        ...styles[variant],
      }}
    >
      {icon && <span style={{ display: 'inline-flex' }}>{icon}</span>}
      <span>{children}</span>
    </span>
  )
}
