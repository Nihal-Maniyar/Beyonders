import { useState, useEffect } from 'react'
import { AppShell } from './components/layout/AppShell'
import { StageKey } from './types'
import { WelcomeView } from './components/views/WelcomeView'
import { PreAssessmentView } from './components/views/PreAssessmentView'
import { LessonView } from './components/views/LessonView'
import { PracticeView } from './components/views/PracticeView'
import { RemediationView } from './components/views/RemediationView'
import { TeachBackView } from './components/views/TeachBackView'
import { PostAssessmentView } from './components/views/PostAssessmentView'
import { ProgressReportView } from './components/views/ProgressReportView'
import { api } from './services/api'

export default function App() {
  const [currentStage, setCurrentStage] = useState<StageKey>('WELCOME')
  const [unlockedStages, setUnlockedStages] = useState<Set<StageKey>>(new Set(['WELCOME']))
  const [completedStages, setCompletedStages] = useState<Set<StageKey>>(new Set())
  const [studentName, setStudentName] = useState('Alex')
  const [learnerId, setLearnerId] = useState('learner_react_student_01')
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const [remediationActivityId, setRemediationActivityId] = useState<string>('A_FRACTION_STRIPS')

  // Initialize or synchronize learner session on mount or name change
  useEffect(() => {
    async function initSession() {
      try {
        const id = `learner_${studentName.toLowerCase().replace(/[^a-z0-9]/g, '') || 'guest'}_01`
        setLearnerId(id)
        const sessionData = await api.createLearnerSession(id, studentName)
        setSessionId(sessionData.session_id)
      } catch (err) {
        console.warn('Backend API session init notice (running offline or during test):', err)
      }
    }
    initSession()
  }, [studentName])

  const unlockAndAdvance = (next: StageKey) => {
    setCompletedStages((prev) => new Set([...prev, currentStage]))
    setUnlockedStages((prev) => new Set([...prev, next]))
    setCurrentStage(next)
  }

  const handleResetSession = () => {
    setCurrentStage('WELCOME')
    setUnlockedStages(new Set(['WELCOME']))
    setCompletedStages(new Set())
  }

  const handleGoToRemediation = (actId: string) => {
    setRemediationActivityId(actId)
    setUnlockedStages((prev) => new Set([...prev, 'REMEDIATION']))
    setCurrentStage('REMEDIATION')
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
            onStartPreAssessment={() => unlockAndAdvance('PRE_ASSESSMENT')}
          />
        )}

        {currentStage === 'PRE_ASSESSMENT' && (
          <PreAssessmentView
            learnerId={learnerId}
            sessionId={sessionId}
            onComplete={() => unlockAndAdvance('LESSON')}
          />
        )}

        {currentStage === 'LESSON' && (
          <LessonView
            onProceedToPractice={() => unlockAndAdvance('PRACTICE')}
          />
        )}

        {currentStage === 'PRACTICE' && (
          <PracticeView
            learnerId={learnerId}
            sessionId={sessionId}
            onGoToRemediation={handleGoToRemediation}
            onProceedToTeachBack={() => unlockAndAdvance('TEACH_BACK')}
          />
        )}

        {currentStage === 'REMEDIATION' && (
          <RemediationView
            activityId={remediationActivityId}
            onProceedToTeachBack={() => unlockAndAdvance('TEACH_BACK')}
          />
        )}

        {currentStage === 'TEACH_BACK' && (
          <TeachBackView
            learnerId={learnerId}
            sessionId={sessionId}
            onProceedToPostAssessment={() => unlockAndAdvance('POST_ASSESSMENT')}
          />
        )}

        {currentStage === 'POST_ASSESSMENT' && (
          <PostAssessmentView
            learnerId={learnerId}
            sessionId={sessionId}
            onComplete={() => unlockAndAdvance('PROGRESS_REPORT')}
          />
        )}

        {currentStage === 'PROGRESS_REPORT' && (
          <ProgressReportView
            learnerId={learnerId}
            onStartFreshSession={handleResetSession}
          />
        )}
      </div>
    </AppShell>
  )
}
