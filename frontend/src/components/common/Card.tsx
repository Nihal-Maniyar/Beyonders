import React from 'react'

export interface CardProps {
  children: React.ReactNode
  title?: React.ReactNode
  subtitle?: React.ReactNode
  badge?: React.ReactNode
  accent?: 'brand' | 'success' | 'misconception' | 'socratic' | 'warning' | 'none'
  footer?: React.ReactNode
  className?: string
  style?: React.CSSProperties
  onClick?: () => void
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  badge,
  accent = 'none',
  footer,
  className = '',
  style,
  onClick,
}) => {
  const accentBorders: Record<string, string> = {
    brand: '4px solid var(--color-brand)',
    success: '4px solid var(--color-success)',
    misconception: '4px solid var(--color-misconception)',
    socratic: '4px solid var(--color-socratic)',
    warning: '4px solid var(--color-warning)',
    none: 'none',
  }

  return (
    <div
      className={`card-base ${className}`}
      onClick={onClick}
      style={{
        borderLeft: accentBorders[accent] !== 'none' ? accentBorders[accent] : undefined,
        cursor: onClick ? 'pointer' : 'default',
        padding: '20px 24px',
        ...style,
      }}
    >
      {(title || badge) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '12px',
            marginBottom: subtitle ? '4px' : '16px',
          }}
        >
          {title && (
            <h3
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.25rem',
                color: 'var(--color-text-primary)',
                margin: 0,
              }}
            >
              {title}
            </h3>
          )}
          {badge && <div>{badge}</div>}
        </div>
      )}

      {subtitle && (
        <p
          style={{
            fontSize: '0.9rem',
            color: 'var(--color-text-secondary)',
            marginBottom: '16px',
          }}
        >
          {subtitle}
        </p>
      )}

      <div>{children}</div>

      {footer && (
        <div
          style={{
            marginTop: '20px',
            paddingTop: '16px',
            borderTop: '1px solid var(--color-border)',
          }}
        >
          {footer}
        </div>
      )}
    </div>
  )
}
