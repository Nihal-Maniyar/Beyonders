import React from 'react'
import { StageKey } from '../../types'

export interface StageStepperProps {
  currentStage: StageKey
  unlockedStages: Set<StageKey>
  completedStages: Set<StageKey>
  onSelectStage: (stage: StageKey) => void
}

interface StageConfig {
  key: StageKey
  label: string
  shortLabel: string
  icon: string
  description: string
}

const STAGES: StageConfig[] = [
  { key: 'WELCOME', label: '1. Syllabus & Goals', shortLabel: 'Goals', icon: '📖', description: 'Curriculum overview' },
  { key: 'PRE_ASSESSMENT', label: '2. Baseline Check', shortLabel: 'Pre-Test', icon: '📝', description: 'Diagnostic baseline' },
  { key: 'LESSON', label: '3. Concept Lessons', shortLabel: 'Lessons', icon: '💡', description: 'Worked examples' },
  { key: 'PRACTICE', label: '4. Diagnostic Practice', shortLabel: 'Practice', icon: '🎯', description: 'Reasoning check' },
  { key: 'REMEDIATION', label: '5. Targeted Remediation', shortLabel: 'Remedy', icon: '🛠️', description: 'Visual tools' },
  { key: 'TEACH_BACK', label: '6. Student Teach-Back', shortLabel: 'Teach-Back', icon: '🗣️', description: 'Rubric grading' },
  { key: 'POST_ASSESSMENT', label: '7. Final Assessment', shortLabel: 'Post-Test', icon: '🏁', description: 'Growth measurement' },
  { key: 'PROGRESS_REPORT', label: '8. Mastery Report', shortLabel: 'Report', icon: '📊', description: 'Learning gains' },
]

export const StageStepper: React.FC<StageStepperProps> = ({
  currentStage,
  unlockedStages,
  completedStages,
  onSelectStage,
}) => {
  return (
    <nav
      style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid var(--color-border)',
        overflowX: 'auto',
        WebkitOverflowScrolling: 'touch',
      }}
      aria-label="Learning Stages"
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          minWidth: 'max-content',
        }}
      >
        {STAGES.map((stage, idx) => {
          const isCurrent = currentStage === stage.key
          const isUnlocked = unlockedStages.has(stage.key)
          const isCompleted = completedStages.has(stage.key)

          return (
            <React.Fragment key={stage.key}>
              <button
                onClick={() => isUnlocked && onSelectStage(stage.key)}
                disabled={!isUnlocked}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: isCurrent
                    ? '2px solid var(--color-brand)'
                    : isCompleted
                    ? '1.5px solid var(--color-success-border)'
                    : '1px solid var(--color-border)',
                  backgroundColor: isCurrent
                    ? 'var(--color-brand-light)'
                    : isCompleted
                    ? 'var(--color-success-bg)'
                    : '#ffffff',
                  color: isCurrent
                    ? 'var(--color-brand)'
                    : isCompleted
                    ? 'var(--color-success-dark)'
                    : isUnlocked
                    ? 'var(--color-text-secondary)'
                    : 'var(--color-text-muted)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.875rem',
                  fontWeight: isCurrent ? 700 : 600,
                  cursor: isUnlocked ? 'pointer' : 'not-allowed',
                  opacity: isUnlocked ? 1 : 0.45,
                  transition: 'all var(--transition-fast)',
                  whiteSpace: 'nowrap',
                }}
              >
                <span>{stage.icon}</span>
                <span>{stage.shortLabel}</span>
                {isCompleted && <span style={{ color: 'var(--color-success)', fontSize: '0.75rem' }}>✓</span>}
              </button>

              {idx < STAGES.length - 1 && (
                <span
                  style={{
                    color: isCompleted ? 'var(--color-success-border)' : '#cbd5e1',
                    fontSize: '0.8rem',
                    userSelect: 'none',
                  }}
                >
                  ➔
                </span>
              )}
            </React.Fragment>
          )
        })}
      </div>
    </nav>
  )
}
