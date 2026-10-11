import React from 'react'
import { FractionBar } from './FractionBar'

export interface FractionCompareProps {
  fractionA: { numerator: number; denominator: number; label?: string }
  fractionB: { numerator: number; denominator: number; label?: string }
  title?: string
}

export const FractionCompare: React.FC<FractionCompareProps> = ({
  fractionA,
  fractionB,
  title,
}) => {
  const valueA = fractionA.numerator / Math.max(1, fractionA.denominator)
  const valueB = fractionB.numerator / Math.max(1, fractionB.denominator)

  const relation =
    Math.abs(valueA - valueB) < 0.0001
      ? 'are EQUAL to'
      : valueA > valueB
      ? 'is GREATER than'
      : 'is LESS than'

  return (
    <div
      style={{
        background: '#ffffff',
        border: '1.5px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: '20px',
        boxShadow: 'var(--shadow-sm)',
        margin: '16px 0',
      }}
    >
      {title && (
        <h4
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.1rem',
            color: 'var(--color-text-primary)',
            marginBottom: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span>⚖️</span>
          <span>{title}</span>
        </h4>
      )}

      {/* Bar A */}
      <FractionBar
        numerator={fractionA.numerator}
        denominator={fractionA.denominator}
        label={fractionA.label || `Fraction A: ${fractionA.numerator}/${fractionA.denominator}`}
        color="#f59e0b"
      />

      {/* Bar B */}
      <FractionBar
        numerator={fractionB.numerator}
        denominator={fractionB.denominator}
        label={fractionB.label || `Fraction B: ${fractionB.numerator}/${fractionB.denominator}`}
        color="#0284c7"
      />

      <div
        style={{
          marginTop: '16px',
          padding: '10px 14px',
          backgroundColor: '#f8fafc',
          borderRadius: 'var(--radius-md)',
          border: '1px solid #e2e8f0',
          fontFamily: 'var(--font-display)',
          fontSize: '0.95rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span>
          Visual Comparison: <strong>{fractionA.numerator}/{fractionA.denominator}</strong> {relation}{' '}
          <strong>{fractionB.numerator}/{fractionB.denominator}</strong>
        </span>
        <span
          style={{
            fontSize: '0.85rem',
            color: '#64748b',
          }}
        >
          Notice: Each whole unit has identical total length!
        </span>
      </div>
    </div>
  )
}
