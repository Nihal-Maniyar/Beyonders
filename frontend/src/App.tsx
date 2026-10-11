import { useState } from 'react'
import { AppShell } from './components/layout/AppShell'
import { StageKey } from './types'
import { Card } from './components/common/Card'
import { Button } from './components/common/Button'
import { Badge } from './components/common/Badge'
import { Callout } from './components/common/Callout'
import { FractionCompare } from './components/visuals/FractionCompare'

export default function App() {
  const [currentStage, setCurrentStage] = useState<StageKey>('WELCOME')
  const [unlockedStages, setUnlockedStages] = useState<Set<StageKey>>(new Set(['WELCOME', 'PRE_ASSESSMENT']))
  const [completedStages, setCompletedStages] = useState<Set<StageKey>>(new Set())
  const [studentName, setStudentName] = useState('Alex')

  const handleResetSession = () => {
    setCurrentStage('WELCOME')
    setUnlockedStages(new Set(['WELCOME', 'PRE_ASSESSMENT']))
    setCompletedStages(new Set())
  }

  const unlockNext = (next: StageKey) => {
    setCompletedStages(prev => new Set([...prev, currentStage]))
    setUnlockedStages(prev => new Set([...prev, next]))
    setCurrentStage(next)
  }

  return (
    <AppShell
      currentStage={currentStage}
      unlockedStages={unlockedStages}
      completedStages={completedStages}
      studentName={studentName}
      onStudentNameChange={setStudentName}
      onSelectStage={setCurrentStage}
      onResetSession={handleResetSession}
    >
      <div className="animate-fade-in">
        {currentStage === 'WELCOME' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
            <Card
              title={`Welcome to LearnLoop AI Fractions Studio, ${studentName}!`}
              subtitle="An adaptive mathematical learning environment that diagnoses reasoning, not just final answers."
              badge={<Badge variant="success">Active Session</Badge>}
            >
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', margin: '16px 0' }}>
                <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ fontFamily: 'var(--font-display)', marginBottom: '8px' }}>🎯 What We Investigate</h4>
                  <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                    We explore <em>how you think</em> about fractions: denominator part sizes, numerator counts, and proportional equivalence.
                  </p>
                </div>
                <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ fontFamily: 'var(--font-display)', marginBottom: '8px' }}>🛠️ Targeted Remediation</h4>
                  <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                    If a misconception is detected (such as whole-number bias), you receive custom visual tools to anchor your intuition.
                  </p>
                </div>
                <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ fontFamily: 'var(--font-display)', marginBottom: '8px' }}>🗣️ Teach-Back Rubric</h4>
                  <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                    Explain concepts in your own words. We evaluate your explanation against 5 clear criteria (R1–R5).
                  </p>
                </div>
              </div>

              {/* Fraction comparison showcase */}
              <FractionCompare
                title="Preview: Comparing Fractions with Same Numerator (2/5 vs 2/3)"
                fractionA={{ numerator: 2, denominator: 5, label: '2 fifths (2/5)' }}
                fractionB={{ numerator: 2, denominator: 3, label: '2 thirds (2/3)' }}
              />

              <Callout type="teacher">
                LearnLoop AI supports classroom educators by providing diagnostic visibility into common misconceptions (M1 Whole-Number Bias, M2 Inverted Denominators, M3 Numerator-Only comparison).
              </Callout>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
                <Button size="lg" onClick={() => unlockNext('PRE_ASSESSMENT')}>
                  Start Baseline Pre-Assessment ➔
                </Button>
              </div>
            </Card>
          </div>
        )}

        {currentStage !== 'WELCOME' && (
          <Card
            title={`Stage: ${currentStage}`}
            subtitle="Stage view active. Full views connected in subsequent milestones."
          >
            <p style={{ color: '#64748b', margin: '20px 0' }}>
              Navigation and core design system functional.
            </p>
            <Button variant="secondary" onClick={() => setCurrentStage('WELCOME')}>
              ⬅️ Back to Welcome
            </Button>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
