import React from 'react'

export interface FractionBarProps {
  numerator: number
  denominator: number
  color?: string
  label?: string
  showLabels?: boolean
  height?: number
  interactive?: boolean
  onSliceClick?: (index: number) => void
}

export const FractionBar: React.FC<FractionBarProps> = ({
  numerator,
  denominator,
  color = 'var(--color-numerator)',
  label,
  showLabels = true,
  height = 42,
  interactive = false,
  onSliceClick,
}) => {
  const safeDenominator = Math.max(1, denominator)
  const safeNumerator = Math.min(Math.max(0, numerator), safeDenominator)

  return (
    <div style={{ width: '100%', margin: '12px 0' }}>
      {(label || showLabels) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            marginBottom: '6px',
            fontFamily: 'var(--font-display)',
            fontSize: '0.95rem',
            color: 'var(--color-text-primary)',
          }}
        >
          <span>{label || `${safeNumerator} out of ${safeDenominator} equal parts`}</span>
          <span style={{ fontWeight: 700, color: 'var(--color-brand)' }}>
            {safeNumerator}/{safeDenominator}
          </span>
        </div>
      )}

      {/* Whole unit bar */}
      <div
        style={{
          display: 'flex',
          width: '100%',
          height: `${height}px`,
          backgroundColor: '#f1f5f9',
          border: '2px solid #cbd5e1',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.06)',
          position: 'relative',
        }}
        role="progressbar"
        aria-valuenow={safeNumerator}
        aria-valuemin={0}
        aria-valuemax={safeDenominator}
        aria-label={`${safeNumerator} of ${safeDenominator}`}
      >
        {Array.from({ length: safeDenominator }).map((_, idx) => {
          const isShaded = idx < safeNumerator
          return (
            <div
              key={idx}
              onClick={() => interactive && onSliceClick && onSliceClick(idx)}
              style={{
                flex: 1,
                borderRight: idx < safeDenominator - 1 ? '1.5px solid #94a3b8' : 'none',
                backgroundColor: isShaded ? color : 'transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: interactive ? 'pointer' : 'default',
                transition: 'background-color var(--transition-fast)',
                position: 'relative',
              }}
              title={`Unit piece 1/${safeDenominator} (part ${idx + 1} of ${safeDenominator})`}
            >
              <span
                style={{
                  fontFamily: 'var(--font-math)',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: isShaded ? '#ffffff' : '#64748b',
                  userSelect: 'none',
                }}
              >
                1/{safeDenominator}
              </span>
            </div>
          )
        })}
      </div>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: '#94a3b8',
          fontFamily: 'var(--font-math)',
          marginTop: '4px',
        }}
      >
        <span>0</span>
        <span>1 Whole</span>
      </div>
    </div>
  )
}
