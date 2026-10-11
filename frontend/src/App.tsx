import { useState, useEffect } from 'react'
import { AppShell } from './components/layout/AppShell'
import { StageKey, ConceptMastery, PrePostReport, ReviewTask } from './types'
import { HomeDashboardView } from './components/views/HomeDashboardView'
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
  const [activeNavTab, setActiveNavTab] = useState<string>('dashboard')
  const [currentStage, setCurrentStage] = useState<StageKey>('WELCOME')
  const [unlockedStages, setUnlockedStages] = useState<Set<StageKey>>(new Set(['WELCOME', 'LESSON', 'PRACTICE']))
  const [completedStages, setCompletedStages] = useState<Set<StageKey>>(new Set())
  const [studentName, setStudentName] = useState('Alex')
  const [learnerId, setLearnerId] = useState('learner_react_student_01')
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const [remediationActivityId, setRemediationActivityId] = useState<string>('A_FRACTION_STRIPS')

  // Live sidebar info panel states
  const [masteries, setMasteries] = useState<Record<string, ConceptMastery>>({})
  const [report, setReport] = useState<PrePostReport | null>(null)
  const [reviews, setReviews] = useState<ReviewTask[]>([])

  // Refresh data function
  const refreshLearnerData = async (lId: string) => {
    try {
      const [mas, rep, rev] = await Promise.allSettled([
        api.getMastery(lId),
        api.getReport(lId),
        api.getReviewTasks(lId),
      ])
      if (mas.status === 'fulfilled') setMasteries(mas.value)
      if (rep.status === 'fulfilled') setReport(rep.value)
      if (rev.status === 'fulfilled') setReviews(rev.value)
    } catch {
      // offline silent fallback
    }
  }

  // Initialize or synchronize learner session on mount or name change
  useEffect(() => {
    async function initSession() {
      try {
        const id = `learner_${studentName.toLowerCase().replace(/[^a-z0-9]/g, '') || 'guest'}_01`
        setLearnerId(id)
        const sessionData = await api.createLearnerSession(id, studentName)
        setSessionId(sessionData.session_id)
        refreshLearnerData(id)
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
    setActiveNavTab(
      next === 'LESSON'
        ? 'learn'
        : next === 'PRACTICE'
        ? 'practice'
        : next === 'REMEDIATION'
        ? 'remediation'
        : next === 'TEACH_BACK'
        ? 'teachback'
        : next === 'PRE_ASSESSMENT'
        ? 'pre_assessment'
        : next === 'POST_ASSESSMENT'
        ? 'post_assessment'
        : next === 'PROGRESS_REPORT'
        ? 'progress'
        : 'dashboard'
    )
    refreshLearnerData(learnerId)
  }

  const handleResetSession = () => {
    setCurrentStage('WELCOME')
    setActiveNavTab('dashboard')
    setUnlockedStages(new Set(['WELCOME', 'LESSON', 'PRACTICE']))
    setCompletedStages(new Set())
    setMasteries({})
    setReport(null)
    setReviews([])
  }

  const handleGoToRemediation = (actId: string) => {
    setRemediationActivityId(actId)
    setUnlockedStages((prev) => new Set([...prev, 'REMEDIATION']))
    setCurrentStage('REMEDIATION')
    setActiveNavTab('remediation')
    refreshLearnerData(learnerId)
  }

  return (
    <AppShell
      currentStage={currentStage}
      unlockedStages={unlockedStages}
      completedStages={completedStages}
      studentName={studentName}
      learnerId={learnerId}
      activeNavTab={activeNavTab}
      masteries={masteries}
      report={report}
      reviews={reviews}
      onStudentNameChange={setStudentName}
      onSelectNavTab={setActiveNavTab}
      onSelectStage={setCurrentStage}
      onResetSession={handleResetSession}
    >
      <div className="animate-fade-in">
        {activeNavTab === 'dashboard' && (
          <HomeDashboardView
            studentName={studentName}
            currentStage={currentStage}
            onNavigateToStage={(stage) => {
              setCurrentStage(stage)
              setActiveNavTab(
                stage === 'LESSON'
                  ? 'learn'
                  : stage === 'PRACTICE'
                  ? 'practice'
                  : stage === 'PRE_ASSESSMENT'
                  ? 'pre_assessment'
                  : stage === 'POST_ASSESSMENT'
                  ? 'post_assessment'
                  : stage === 'TEACH_BACK'
                  ? 'teachback'
                  : stage === 'PROGRESS_REPORT'
                  ? 'progress'
                  : 'dashboard'
              )
            }}
          />
        )}

        {activeNavTab !== 'dashboard' && currentStage === 'WELCOME' && (
          <WelcomeView
            studentName={studentName}
            onStartPreAssessment={() => unlockAndAdvance('PRE_ASSESSMENT')}
          />
        )}

        {(activeNavTab === 'pre_assessment' || (activeNavTab !== 'dashboard' && currentStage === 'PRE_ASSESSMENT')) && (
          <PreAssessmentView
            learnerId={learnerId}
            sessionId={sessionId}
            onComplete={() => unlockAndAdvance('LESSON')}
          />
        )}

        {(activeNavTab === 'learn' || (activeNavTab !== 'dashboard' && currentStage === 'LESSON')) && (
          <LessonView
            onProceedToPractice={() => unlockAndAdvance('PRACTICE')}
          />
        )}

        {(activeNavTab === 'practice' || (activeNavTab !== 'dashboard' && currentStage === 'PRACTICE')) && (
          <PracticeView
            learnerId={learnerId}
            sessionId={sessionId}
            onGoToRemediation={handleGoToRemediation}
            onProceedToTeachBack={() => unlockAndAdvance('TEACH_BACK')}
          />
        )}

        {(activeNavTab === 'remediation' || (activeNavTab !== 'dashboard' && currentStage === 'REMEDIATION')) && (
          <RemediationView
            activityId={remediationActivityId}
            onProceedToTeachBack={() => unlockAndAdvance('TEACH_BACK')}
          />
        )}

        {(activeNavTab === 'teachback' || (activeNavTab !== 'dashboard' && currentStage === 'TEACH_BACK')) && (
          <TeachBackView
            learnerId={learnerId}
            sessionId={sessionId}
            onProceedToPostAssessment={() => unlockAndAdvance('POST_ASSESSMENT')}
          />
        )}

        {(activeNavTab === 'post_assessment' || (activeNavTab !== 'dashboard' && currentStage === 'POST_ASSESSMENT')) && (
          <PostAssessmentView
            learnerId={learnerId}
            sessionId={sessionId}
            onComplete={() => unlockAndAdvance('PROGRESS_REPORT')}
          />
        )}

        {(activeNavTab === 'progress' || (activeNavTab !== 'dashboard' && currentStage === 'PROGRESS_REPORT')) && (
          <ProgressReportView
            learnerId={learnerId}
            onStartFreshSession={handleResetSession}
          />
        )}
      </div>
    </AppShell>
  )
}
