import React from 'react'

export interface CalloutProps {
  title?: string
  children: React.ReactNode
  type?: 'teacher' | 'misconception' | 'socratic' | 'success' | 'info'
  icon?: React.ReactNode
}

export const Callout: React.FC<CalloutProps> = ({
  title,
  children,
  type = 'info',
  icon,
}) => {
  const styles: Record<string, { bg: string; border: string; text: string; iconColor: string; defaultTitle: string; defaultIcon: string }> = {
    teacher: {
      bg: '#f0fdf4',
      border: '#86efac',
      text: '#166534',
      iconColor: '#15803d',
      defaultTitle: 'Teacher Note & Curriculum Grounding',
      defaultIcon: '👩‍🏫',
    },
    misconception: {
      bg: 'var(--color-misconception-bg)',
      border: 'var(--color-misconception-border)',
      text: 'var(--color-misconception-dark)',
      iconColor: 'var(--color-misconception)',
      defaultTitle: 'Misconception Detected',
      defaultIcon: '💡',
    },
    socratic: {
      bg: 'var(--color-socratic-bg)',
      border: 'var(--color-socratic-border)',
      text: 'var(--color-socratic-dark)',
      iconColor: 'var(--color-socratic)',
      defaultTitle: 'Tutor Clarification Question',
      defaultIcon: '🤔',
    },
    success: {
      bg: 'var(--color-success-bg)',
      border: 'var(--color-success-border)',
      text: 'var(--color-success-dark)',
      iconColor: 'var(--color-success)',
      defaultTitle: 'Sound Mathematical Reasoning',
      defaultIcon: '🎉',
    },
    info: {
      bg: 'var(--color-brand-light)',
      border: 'var(--color-brand-border)',
      text: '#1e40af',
      iconColor: 'var(--color-brand)',
      defaultTitle: 'Learning Insight',
      defaultIcon: '📌',
    },
  }

  const current = styles[type]

  return (
    <div
      style={{
        backgroundColor: current.bg,
        border: `1.5px solid ${current.border}`,
        borderRadius: 'var(--radius-md)',
        padding: '16px 20px',
        margin: '16px 0',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontFamily: 'var(--font-display)',
          fontWeight: 700,
          color: current.text,
          marginBottom: '8px',
          fontSize: '1rem',
        }}
      >
        <span style={{ fontSize: '1.25rem' }}>{icon || current.defaultIcon}</span>
        <span>{title || current.defaultTitle}</span>
      </div>
      <div style={{ color: current.text, fontSize: '0.95rem', lineHeight: 1.6 }}>
        {children}
      </div>
    </div>
  )
}
