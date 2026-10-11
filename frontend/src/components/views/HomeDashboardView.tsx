import React, { useState } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { FractionCompare } from '../visuals/FractionCompare'
import { FractionExplorer } from '../visuals/FractionExplorer'
import { StageKey } from '../../types'

export interface HomeDashboardViewProps {
  studentName: string
  currentStage: StageKey
  onNavigateToStage: (stage: StageKey) => void
}

export const HomeDashboardView: React.FC<HomeDashboardViewProps> = ({
  studentName,
  currentStage,
  onNavigateToStage,
}) => {
  const [askPrompt, setAskPrompt] = useState('')
  const [aiResponse, setAiResponse] = useState<string | null>(null)
  const [activeDiagram, setActiveDiagram] = useState<boolean>(false)

  const handleAskLearnLoop = (e: React.FormEvent) => {
    e.preventDefault()
    if (!askPrompt.trim()) return

    const lower = askPrompt.toLowerCase()
    if (lower.includes('2/5') || lower.includes('2/3') || lower.includes('larger') || lower.includes('compare')) {
      setAiResponse(
        `Great question! When comparing 2/5 and 2/3, notice that both have the same numerator (2 parts). However, dividing a whole into 3 equal parts yields much bigger slices than dividing it into 5 parts. Therefore, 2/3 is greater than 2/5!`
      )
      setActiveDiagram(true)
    } else if (lower.includes('denominator') || lower.includes('bottom')) {
      setAiResponse(
        `The denominator (bottom number) represents the total number of equal parts the whole is cut into. The more slices you make, the smaller each slice becomes!`
      )
    } else if (lower.includes('numerator') || lower.includes('top')) {
      setAiResponse(
        `The numerator (top number) counts how many of those equal parts are chosen or shaded. For example, in 3/4, you have 3 slices out of 4.`
      )
    } else if (lower.includes('equivalent') || lower.includes('equal')) {
      setAiResponse(
        `Two fractions are equivalent if they show the exact same amount of the whole. You can find equivalent fractions by multiplying or dividing top and bottom by the same number (e.g. 1/2 = 2/4).`
      )
    } else {
      setAiResponse(
        `LearnLoop Fraction Assistant: In fractions, remember our golden rule: always compare wholes of the same size, and remember that more cuts mean smaller pieces! Try one of the quick actions below to explore.`
      )
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Welcome Banner Card */}
      <div
        style={{
          background: 'linear-gradient(135deg, #fff7ed 0%, #fffdfa 50%, #ffffff 100%)',
          border: '1.5px solid var(--color-brand-border)',
          borderRadius: 'var(--radius-xl)',
          padding: '28px 32px',
          boxShadow: 'var(--shadow-sm)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{ maxWidth: '640px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Badge variant="brand" size="sm">Fractions Studio</Badge>
            <span style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
              Current Step: <strong>{currentStage.replace(/_/g, ' ')}</strong>
            </span>
          </div>
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '2rem',
              color: 'var(--color-text-primary)',
              margin: '0 0 10px 0',
              lineHeight: 1.2,
            }}
          >
            Welcome back, {studentName}! 🌟
          </h2>
          <p style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: '0 0 20px 0' }}>
            Ready to explore fraction comparisons? We analyze <strong>how you reason</strong>, detect subtle misconceptions like whole-number bias, and use tactile visual models to build genuine mathematical intuition.
          </p>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <Button size="md" variant="primary" onClick={() => onNavigateToStage('PRE_ASSESSMENT')}>
              📝 Start Baseline Pre-Test
            </Button>
            <Button size="md" variant="secondary" onClick={() => onNavigateToStage('LESSON')}>
              📖 Review Worked Lessons
            </Button>
          </div>
        </div>
      </div>

      {/* Ask LearnLoop Question Input */}
      <Card
        title="💬 Ask LearnLoop AI"
        subtitle="Have a question about fraction pieces, numerators, or denominators? Ask the studio assistant."
        accent="brand"
      >
        <form onSubmit={handleAskLearnLoop} style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={askPrompt}
            onChange={(e) => setAskPrompt(e.target.value)}
            placeholder="e.g. 'Why is 2/3 bigger than 2/5?' or 'What does the denominator mean?'"
            style={{
              flex: 1,
              minWidth: '240px',
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              border: '1.5px solid var(--color-border)',
              fontFamily: 'var(--font-body)',
              fontSize: '0.95rem',
              outline: 'none',
              backgroundColor: 'var(--color-canvas)',
            }}
          />
          <Button type="submit" variant="primary" size="md">
            Ask Assistant ✨
          </Button>
        </form>

        {aiResponse && (
          <div style={{ marginTop: '16px' }}>
            <Callout type="teacher" title="LearnLoop Pedagogical Explanation">
              <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.6 }}>{aiResponse}</p>
            </Callout>
          </div>
        )}
      </Card>

      {/* Quick Action Tiles */}
      <div>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', color: 'var(--color-text-primary)', marginBottom: '14px' }}>
          ⚡ Quick Learning Actions
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          {/* Action 1 */}
          <div
            onClick={() => onNavigateToStage('LESSON')}
            style={{
              backgroundColor: '#ffffff',
              border: '1.5px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: '18px',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              boxShadow: 'var(--shadow-sm)',
            }}
            className="card-base"
          >
            <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>💡</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
              Explain Fractions
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
              Step-by-step visual lessons on C1, C2, and C3 concepts.
            </p>
          </div>

          {/* Action 2 */}
          <div
            onClick={() => onNavigateToStage('PRACTICE')}
            style={{
              backgroundColor: '#ffffff',
              border: '1.5px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: '18px',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              boxShadow: 'var(--shadow-sm)',
            }}
            className="card-base"
          >
            <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>🎯</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
              Quiz Me (Practice)
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
              Answer diagnostic questions and explain your mathematical reasoning.
            </p>
          </div>

          {/* Action 3 */}
          <div
            onClick={() => setActiveDiagram(!activeDiagram)}
            style={{
              backgroundColor: '#ffffff',
              border: '1.5px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: '18px',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              boxShadow: 'var(--shadow-sm)',
            }}
            className="card-base"
          >
            <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>⚖️</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
              Show Diagram
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
              Toggle interactive comparative fraction strips (2/5 vs 2/3).
            </p>
          </div>

          {/* Action 4 */}
          <div
            onClick={() => onNavigateToStage('TEACH_BACK')}
            style={{
              backgroundColor: '#ffffff',
              border: '1.5px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: '18px',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              boxShadow: 'var(--shadow-sm)',
            }}
            className="card-base"
          >
            <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>🗣️</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
              Teach-Back Studio
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
              Explain concepts in your own words for standardized rubric grading.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Visual Comparative Diagram (Triggered by quick action or question) */}
      {activeDiagram && (
        <FractionCompare
          title="Tactile Model: Why 2/3 is Larger than 2/5"
          fractionA={{ numerator: 2, denominator: 5, label: '2/5 (Whole cut into 5 smaller pieces)' }}
          fractionB={{ numerator: 2, denominator: 3, label: '2/3 (Whole cut into 3 bigger pieces)' }}
        />
      )}

      {/* Interactive Fraction Laboratory */}
      <FractionExplorer />
    </div>
  )
}
