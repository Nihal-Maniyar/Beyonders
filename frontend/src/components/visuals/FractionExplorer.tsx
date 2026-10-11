import React, { useState } from 'react'
import { FractionBar } from './FractionBar'
import { Button } from '../common/Button'

export const FractionExplorer: React.FC = () => {
  const [num, setNum] = useState(2)
  const [den, setDen] = useState(5)

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1.5px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        margin: '20px 0',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', margin: 0 }}>
            🎛️ Interactive Fraction Laboratory
          </h4>
          <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '2px 0 0 0' }}>
            Adjust the top and bottom numbers to observe how part size and count change.
          </p>
        </div>

        {/* Fraction Display */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#f8fafc',
            border: '2px solid #e2e8f0',
            borderRadius: 'var(--radius-md)',
            padding: '8px 16px',
          }}
        >
          <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Your Fraction:</span>
          <div className="fraction-inline" style={{ fontSize: '1.4rem', color: 'var(--color-brand)' }}>
            <span className="num">{num}</span>
            <span className="den">{den}</span>
          </div>
        </div>
      </div>

      {/* Sliders / Tactile Steppers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        {/* Numerator control */}
        <div style={{ background: 'var(--color-numerator-bg)', border: '1px solid var(--color-numerator-border)', borderRadius: 'var(--radius-md)', padding: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-numerator)' }}>
              Top (Numerator): Parts Shaded
            </span>
            <span style={{ fontFamily: 'var(--font-math)', fontWeight: 700, color: 'var(--color-numerator)' }}>
              {num}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <Button size="sm" variant="secondary" onClick={() => setNum(Math.max(0, num - 1))} disabled={num <= 0}>
              -
            </Button>
            <input
              type="range"
              min="0"
              max={den}
              value={num}
              onChange={(e) => setNum(Number(e.target.value))}
              style={{ flex: 1, accentColor: '#d97706' }}
            />
            <Button size="sm" variant="secondary" onClick={() => setNum(Math.min(den, num + 1))} disabled={num >= den}>
              +
            </Button>
          </div>
        </div>

        {/* Denominator control */}
        <div style={{ background: 'var(--color-denominator-bg)', border: '1px solid var(--color-denominator-border)', borderRadius: 'var(--radius-md)', padding: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-denominator)' }}>
              Bottom (Denominator): Total Equal Pieces
            </span>
            <span style={{ fontFamily: 'var(--font-math)', fontWeight: 700, color: 'var(--color-denominator)' }}>
              {den}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <Button size="sm" variant="secondary" onClick={() => { if (den > 1) { setDen(den - 1); setNum(Math.min(num, den - 1)) } }} disabled={den <= 1}>
              -
            </Button>
            <input
              type="range"
              min="1"
              max="12"
              value={den}
              onChange={(e) => {
                const newDen = Number(e.target.value)
                setDen(newDen)
                if (num > newDen) setNum(newDen)
              }}
              style={{ flex: 1, accentColor: '#0284c7' }}
            />
            <Button size="sm" variant="secondary" onClick={() => setDen(Math.min(12, den + 1))} disabled={den >= 12}>
              +
            </Button>
          </div>
        </div>
      </div>

      {/* Visual Render */}
      <FractionBar
        numerator={num}
        denominator={den}
        label={`Visual Model: Whole divided into ${den} equal slices, ${num} selected`}
        height={48}
        color="#f59e0b"
      />

      {/* Pedagogical Takeaway */}
      <div
        style={{
          marginTop: '14px',
          padding: '10px 14px',
          backgroundColor: '#f8fafc',
          borderLeft: '4px solid var(--color-brand)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.875rem',
          color: '#334155',
        }}
      >
        <strong>Key Mathematical Principle:</strong> As the denominator ({den}) increases, the whole is shared into more pieces, making <em>each piece smaller</em> (1/{den} is smaller than 1/2)!
      </div>
    </div>
  )
}
