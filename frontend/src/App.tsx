import { useState } from 'react'
import { AppShell } from './components/layout/AppShell'
import { StageKey } from './types'
import { Card } from './components/common/Card'
import { Button } from './components/common/Button'
import { WelcomeView } from './components/views/WelcomeView'
import { LessonView } from './components/views/LessonView'

export default function App() {
  const [currentStage, setCurrentStage] = useState<StageKey>('WELCOME')
  const [unlockedStages, setUnlockedStages] = useState<Set<StageKey>>(new Set(['WELCOME', 'LESSON']))
  const [completedStages, setCompletedStages] = useState<Set<StageKey>>(new Set())
  const [studentName, setStudentName] = useState('Alex')

  const handleResetSession = () => {
    setCurrentStage('WELCOME')
    setUnlockedStages(new Set(['WELCOME', 'LESSON']))
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
          <WelcomeView
            studentName={studentName}
            onStartPreAssessment={() => unlockNext('PRE_ASSESSMENT')}
          />
        )}

        {currentStage === 'LESSON' && (
          <LessonView
            onProceedToPractice={() => unlockNext('PRACTICE')}
          />
        )}

        {currentStage !== 'WELCOME' && currentStage !== 'LESSON' && (
          <Card
            title={`Stage: ${currentStage}`}
            subtitle="Stage view active. Full views connected in subsequent milestones."
          >
            <p style={{ color: '#64748b', margin: '20px 0' }}>
              Core components and views functioning. Assessment and practice workflows connect via API in Milestones D & E.
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <Button variant="secondary" onClick={() => setCurrentStage('WELCOME')}>
                ⬅️ Back to Welcome
              </Button>
              <Button variant="outline" onClick={() => setCurrentStage('LESSON')}>
                💡 View Lessons
              </Button>
            </div>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
