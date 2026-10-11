import {
  Chapter,
  Question,
  DiagnosisResult,
  TeachBackEvaluation,
  PrePostReport,
  RemediationActivity,
  ReviewTask,
} from '../types'

const API_BASE = '/api'

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(`API Error (${res.status}): ${errorText || res.statusText}`)
  }
  return res.json()
}

export const api = {
  async getHealth() {
    return handleResponse<{ status: string; version: string; chapter_loaded: string }>(
      await fetch(`${API_BASE}/health`)
    )
  },

  async getChapter(): Promise<Chapter> {
    return handleResponse<Chapter>(await fetch(`${API_BASE}/chapter`))
  },

  async getFixedAssessmentQuestions(): Promise<Question[]> {
    return handleResponse<Question[]>(await fetch(`${API_BASE}/assessment/fixed`))
  },

  async getQuestion(questionId: string): Promise<Question> {
    return handleResponse<Question>(await fetch(`${API_BASE}/questions/${questionId}`))
  },

  async getActivity(activityId: string): Promise<RemediationActivity> {
    return handleResponse<RemediationActivity>(await fetch(`${API_BASE}/activities/${activityId}`))
  },

  async createLearnerSession(learnerId: string, displayName?: string) {
    return handleResponse<{ learner_id: string; display_name: string; session_id: string; chapter_id: string }>(
      await fetch(`${API_BASE}/learners/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ learner_id: learnerId, display_name: displayName }),
      })
    )
  },

  async startAssessment(learnerId: string, phase: 'pre' | 'post', sessionId?: string) {
    return handleResponse<{ run_id: string; learner_id: string; phase: string; assessment_version: string }>(
      await fetch(`${API_BASE}/assessment/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ learner_id: learnerId, phase, session_id: sessionId }),
      })
    )
  },

  async recordAssessmentAnswer(runId: string, questionId: string, studentAnswer: string) {
    return handleResponse<{ status: string; response_id: string }>(
      await fetch(`${API_BASE}/assessment/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: runId,
          question_id: questionId,
          student_answer: studentAnswer,
        }),
      })
    )
  },

  async completeAssessment(runId: string) {
    return handleResponse<{ status: string; run_id: string }>(
      await fetch(`${API_BASE}/assessment/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ run_id: runId }),
      })
    )
  },

  async diagnosePractice(
    learnerId: string,
    questionId: string,
    studentAnswer: string,
    reasoningText?: string,
    sessionId?: string
  ): Promise<DiagnosisResult> {
    return handleResponse<DiagnosisResult>(
      await fetch(`${API_BASE}/practice/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          learner_id: learnerId,
          question_id: questionId,
          student_answer: studentAnswer,
          reasoning_text: reasoningText,
          session_id: sessionId,
        }),
      })
    )
  },

  async evaluateTeachBack(
    learnerId: string,
    explanation: string,
    sessionId?: string
  ): Promise<TeachBackEvaluation> {
    return handleResponse<TeachBackEvaluation>(
      await fetch(`${API_BASE}/teachback/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          learner_id: learnerId,
          explanation,
          session_id: sessionId,
        }),
      })
    )
  },

  async getReport(learnerId: string): Promise<PrePostReport | null> {
    return handleResponse<PrePostReport | null>(await fetch(`${API_BASE}/reports/${learnerId}`))
  },

  async getMastery(learnerId: string): Promise<Record<string, any>> {
    return handleResponse<Record<string, any>>(await fetch(`${API_BASE}/mastery/${learnerId}`))
  },

  async getReviewTasks(learnerId: string): Promise<ReviewTask[]> {
    return handleResponse<ReviewTask[]>(await fetch(`${API_BASE}/review/${learnerId}`))
  },
}
