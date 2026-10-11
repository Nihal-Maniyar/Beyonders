import React from 'react'
import { Header } from './Header'
import { SidebarNav } from './SidebarNav'
import { RightInfoPanel } from './RightInfoPanel'
import { StageKey, ConceptMastery, PrePostReport, ReviewTask } from '../../types'

export interface AppShellProps {
  children: React.ReactNode
  currentStage: StageKey
  unlockedStages: Set<StageKey>
  completedStages: Set<StageKey>
  studentName: string
  learnerId: string
  activeNavTab: string
  masteries: Record<string, ConceptMastery>
  report: PrePostReport | null
  reviews: ReviewTask[]
  onStudentNameChange: (name: string) => void
  onSelectNavTab: (tabId: string) => void
  onSelectStage: (stage: StageKey) => void
  onResetSession: () => void
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  currentStage,
  unlockedStages,
  completedStages,
  studentName,
  learnerId,
  activeNavTab,
  masteries,
  report,
  reviews,
  onStudentNameChange,
  onSelectNavTab,
  onSelectStage,
  onResetSession,
}) => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-canvas)' }}>
      <Header
        studentName={studentName}
        onStudentNameChange={onStudentNameChange}
        onResetSession={onResetSession}
      />

      {/* 3-Column Studio Dashboard Grid */}
      <div
        style={{
          display: 'flex',
          flex: 1,
          maxWidth: '1600px',
          width: '100%',
          margin: '0 auto',
        }}
      >
        {/* Left Column: Navigation Sidebar */}
        <SidebarNav
          currentStage={currentStage}
          unlockedStages={unlockedStages}
          completedStages={completedStages}
          activeNavTab={activeNavTab}
          onSelectNavTab={onSelectNavTab}
          onSelectStage={onSelectStage}
        />

        {/* Center Column: Main Learning Area */}
        <main
          style={{
            flex: 1,
            minWidth: 0,
            padding: '28px 32px 64px 32px',
          }}
        >
          {children}
        </main>

        {/* Right Column: Information & Mastery Panel */}
        <RightInfoPanel
          studentName={studentName}
          learnerId={learnerId}
          masteries={masteries}
          report={report}
          reviews={reviews}
          onNavigateToStage={(stageId) => {
            onSelectNavTab(stageId)
            const map: Record<string, StageKey> = {
              learn: 'LESSON',
              practice: 'PRACTICE',
              pre_assessment: 'PRE_ASSESSMENT',
              post_assessment: 'POST_ASSESSMENT',
              teachback: 'TEACH_BACK',
              progress: 'PROGRESS_REPORT',
            }
            if (map[stageId]) onSelectStage(map[stageId])
          }}
        />
      </div>

      <footer
        style={{
          borderTop: '1.5px solid var(--color-border)',
          backgroundColor: '#ffffff',
          padding: '16px 24px',
          textAlign: 'center',
          fontSize: '0.85rem',
          color: 'var(--color-text-muted)',
        }}
      >
        <span>
          LearnLoop AI — Adaptive Fractions Learning Studio · Grade 4–6 Mathematics (CCSS.MATH.CONTENT.4.NF.A.2)
        </span>
      </footer>
    </div>
  )
}
