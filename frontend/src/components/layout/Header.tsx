import React from 'react'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'

export interface HeaderProps {
  studentName: string
  onStudentNameChange: (name: string) => void
  onResetSession: () => void
}

export const Header: React.FC<HeaderProps> = ({
  studentName,
  onStudentNameChange,
  onResetSession,
}) => {
  return (
    <header
      style={{
        backgroundColor: '#ffffff',
        borderBottom: '1.5px solid var(--color-border)',
        boxShadow: '0 1px 4px 0 rgba(24, 34, 56, 0.04)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      <div
        style={{
          maxWidth: '1600px',
          margin: '0 auto',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-brand-light)',
              border: '2px solid var(--color-brand-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.4rem',
              boxShadow: 'var(--shadow-tactile)',
            }}
          >
            📐
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.35rem',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                  lineHeight: 1.1,
                }}
              >
                LearnLoop AI
              </span>
              <Badge variant="brand" size="sm">Fractions Studio</Badge>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', margin: 0 }}>
              Adaptive Mathematics Tutor · Grade 4–6
            </p>
          </div>
        </div>

        {/* Center Standards & Quality Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Badge variant="concept" size="sm">CCSS.MATH.4.NF.A.2</Badge>
          <Badge variant="success" size="sm">Deterministic Engine</Badge>
          <Badge variant="neutral" size="sm">Zero Credentials Required</Badge>
        </div>

        {/* Right Student controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
              Student:
            </span>
            <input
              type="text"
              value={studentName}
              onChange={(e) => onStudentNameChange(e.target.value)}
              placeholder="Name"
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 600,
                fontSize: '0.9rem',
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1.5px solid var(--color-border)',
                outline: 'none',
                width: '110px',
                backgroundColor: 'var(--color-canvas)',
              }}
            />
          </div>

          <Button variant="ghost" size="sm" onClick={onResetSession}>
            🔄 Reset
          </Button>
        </div>
      </div>
    </header>
  )
}
