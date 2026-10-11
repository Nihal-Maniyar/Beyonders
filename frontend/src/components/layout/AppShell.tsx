import React from 'react'
import { Header } from './Header'
import { StageStepper } from './StageStepper'
import { StageKey } from '../../types'

export interface AppShellProps {
  children: React.ReactNode
  currentStage: StageKey
  unlockedStages: Set<StageKey>
  completedStages: Set<StageKey>
  studentName: string
  onStudentNameChange: (name: string) => void
  onSelectStage: (stage: StageKey) => void
  onResetSession: () => void
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  currentStage,
  unlockedStages,
  completedStages,
  studentName,
  onStudentNameChange,
  onSelectStage,
  onResetSession,
}) => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        studentName={studentName}
        onStudentNameChange={onStudentNameChange}
        onResetSession={onResetSession}
      />

      <StageStepper
        currentStage={currentStage}
        unlockedStages={unlockedStages}
        completedStages={completedStages}
        onSelectStage={onSelectStage}
      />

      <main
        style={{
          flex: 1,
          maxWidth: '1280px',
          width: '100%',
          margin: '0 auto',
          padding: '24px 20px 64px 20px',
        }}
      >
        {children}
      </main>

      <footer
        style={{
          borderTop: '1px solid var(--color-border)',
          backgroundColor: '#ffffff',
          padding: '16px 24px',
          textAlign: 'center',
          fontSize: '0.85rem',
          color: 'var(--color-text-muted)',
        }}
      >
        <span>LearnLoop AI · VORTEXA 3.0 (Problem Statement E-01) · Common Core CCSS.MATH.CONTENT.4.NF.A.2</span>
      </footer>
    </div>
  )
}
