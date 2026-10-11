import React from 'react'
import { StageKey } from '../../types'

export interface NavItem {
  id: string
  label: string
  icon: string
  description?: string
  stageKey?: StageKey
  isExternal?: boolean
}

export interface SidebarNavProps {
  currentStage: StageKey
  unlockedStages: Set<StageKey>
  completedStages: Set<StageKey>
  activeNavTab: string
  onSelectNavTab: (tabId: string) => void
  onSelectStage: (stage: StageKey) => void
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Home Dashboard', icon: '🏠', description: 'Overview & Quick Actions' },
  { id: 'learn', label: 'Learn Concepts', icon: '📖', stageKey: 'LESSON', description: 'Interactive Worked Examples' },
  { id: 'practice', label: 'Practice & Explore', icon: '🎯', stageKey: 'PRACTICE', description: 'Diagnostic Reasoning' },
  { id: 'remediation', label: 'Remediation Studio', icon: '🛠️', stageKey: 'REMEDIATION', description: 'Visual Models' },
  { id: 'teachback', label: 'Teach-Back Studio', icon: '🗣️', stageKey: 'TEACH_BACK', description: 'Rubric Evaluation' },
  { id: 'pre_assessment', label: 'Baseline Check', icon: '📝', stageKey: 'PRE_ASSESSMENT', description: 'Diagnostic Pre-Test' },
  { id: 'post_assessment', label: 'Final Assessment', icon: '🏁', stageKey: 'POST_ASSESSMENT', description: 'Post-Test Verification' },
  { id: 'progress', label: 'Progress & Mastery', icon: '📊', stageKey: 'PROGRESS_REPORT', description: 'Score Deltas & Review' },
]

export const SidebarNav: React.FC<SidebarNavProps> = ({
  currentStage,
  unlockedStages,
  completedStages,
  activeNavTab,
  onSelectNavTab,
  onSelectStage,
}) => {
  return (
    <aside
      style={{
        width: '260px',
        flexShrink: 0,
        backgroundColor: '#ffffff',
        borderRight: '1.5px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px 16px',
        minHeight: 'calc(100vh - 72px)',
      }}
    >
      <div>
        {/* Navigation Section Title */}
        <div
          style={{
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            fontWeight: 700,
            color: 'var(--color-text-muted)',
            padding: '0 12px 12px 12px',
          }}
        >
          Learning Journey
        </div>

        {/* Navigation Items List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {NAV_ITEMS.map((item) => {
            const isActive =
              activeNavTab === item.id || (item.stageKey && currentStage === item.stageKey && activeNavTab !== 'dashboard')
            const isCompleted = item.stageKey && completedStages.has(item.stageKey)
            const isLocked = item.stageKey && !unlockedStages.has(item.stageKey) && item.stageKey !== 'LESSON' && item.stageKey !== 'PRACTICE'

            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectNavTab(item.id)
                  if (item.stageKey) {
                    onSelectStage(item.stageKey)
                  }
                }}
                disabled={isLocked}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  backgroundColor: isActive ? 'var(--color-brand-light)' : 'transparent',
                  color: isActive ? 'var(--color-brand)' : isLocked ? 'var(--color-text-muted)' : 'var(--color-text-secondary)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.92rem',
                  fontFamily: 'var(--font-display)',
                  textAlign: 'left',
                  cursor: isLocked ? 'not-allowed' : 'pointer',
                  opacity: isLocked ? 0.5 : 1,
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span style={{ fontSize: '1.2rem', lineHeight: 1 }}>{item.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.label}
                  </div>
                </div>
                {isCompleted && (
                  <span
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--color-success)',
                      backgroundColor: 'var(--color-success-bg)',
                      borderRadius: 'var(--radius-full)',
                      padding: '2px 6px',
                    }}
                  >
                    ✓
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Fractions Syllabus Mini-Card */}
        <div
          style={{
            marginTop: '28px',
            padding: '14px',
            backgroundColor: 'var(--color-canvas)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
            Curriculum Strand
          </div>
          <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '4px' }}>
            Grade 4–6 Fractions
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
            Topic: Comparing Fractions (CCSS.4.NF.A.2)
          </div>
          <div style={{ marginTop: '8px', display: 'flex', gap: '4px' }}>
            <span style={{ fontSize: '0.7rem', padding: '2px 6px', backgroundColor: '#e0f2fe', color: '#0369a1', borderRadius: '4px', fontWeight: 600 }}>C1</span>
            <span style={{ fontSize: '0.7rem', padding: '2px 6px', backgroundColor: '#fff7ed', color: '#c2410c', borderRadius: '4px', fontWeight: 600 }}>C2</span>
            <span style={{ fontSize: '0.7rem', padding: '2px 6px', backgroundColor: '#ecfdf5', color: '#047857', borderRadius: '4px', fontWeight: 600 }}>C3</span>
          </div>
        </div>
      </div>

      {/* Offline Status Footer */}
      <div
        style={{
          borderTop: '1px solid var(--color-border)',
          paddingTop: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.78rem',
          color: 'var(--color-text-muted)',
        }}
      >
        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-success)', display: 'inline-block' }} />
        <span>Studio Mode: <strong>100% Offline Active</strong></span>
      </div>
    </aside>
  )
}
