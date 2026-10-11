/**
 * Centralized API client for LearnLoop AI v1 (/api/v1).
 * Strictly handles authentication, error envelopes, and typed responses.
 */

import {
  V1Session,
  V1Lesson,
  V1Assessment,
  V1Attempt,
  V1ProgressSummary,
  V1VoiceResponse,
  V1VoiceEvent,
  V1TutoringInteraction,
  V1Misconception,
  DiagnosisResult,
  TeachBackEvaluation,
} from '../types'

const API_V1_BASE = '/api/v1'
const TOKEN_KEY = 'learnloop_session_token'

export class ApiError extends Error {
  code: string
  details?: unknown[]

  constructor(message: string, code: string = 'UNKNOWN_ERROR', details?: unknown[]) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.details = details
  }
}

class ApiClient {
  private token: string | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = sessionStorage.getItem(TOKEN_KEY)
    }
  }

  setSessionToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(TOKEN_KEY, token)
    }
  }

  getSessionToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = sessionStorage.getItem(TOKEN_KEY)
    }
    return this.token
  }

  clearSessionToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(TOKEN_KEY)
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_V1_BASE}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    }

    const currentToken = this.getSessionToken()
    if (currentToken && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${currentToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      let errPayload: { error?: { code?: string; message?: string; details?: unknown[] } } = {}
      try {
        errPayload = await response.json()
      } catch {
        // Fallback for non-JSON responses
      }

      const errObj = errPayload.error || {}
      throw new ApiError(
        errObj.message || `Request failed with status ${response.status}`,
        errObj.code || `HTTP_${response.status}`,
        errObj.details
      )
    }

    return response.json() as Promise<T>
  }

  // --- Session Management ---

  async createSession(gradeLevel: number = 4): Promise<V1Session> {
    const res = await this.request<{
      session_id: string
      session_token: string
      stage: string
      created_at: string
      expires_at: string
      token?: string
    }>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ grade_level: gradeLevel }),
    })

    const token = res.session_token || res.token || ''
    if (token) {
      this.setSessionToken(token)
    }

    return {
      id: res.session_id,
      token,
      stage: res.stage,
      created_at: res.created_at,
      expires_at: res.expires_at,
    }
  }

  async getCurrentSession(): Promise<V1Session> {
    return this.request<V1Session>('/sessions/current')
  }

  async endCurrentSession(): Promise<{ success: boolean; message: string }> {
    const res = await this.request<{ success: boolean; message: string }>('/sessions/current', {
      method: 'DELETE',
    })
    this.clearSessionToken()
    return res
  }

  // --- Lessons & Curriculum ---

  async getLessons(): Promise<V1Lesson[]> {
    return this.request<V1Lesson[]>('/lessons')
  }

  async getLesson(lessonId: string): Promise<V1Lesson> {
    return this.request<V1Lesson>(`/lessons/${lessonId}`)
  }

  // --- Assessments & Attempts ---

  async getAssessment(code: string): Promise<V1Assessment> {
    return this.request<V1Assessment>(`/assessments/${code}`)
  }

  async startAttempt(assessmentCode: string): Promise<V1Attempt> {
    return this.request<V1Attempt>(`/assessments/${assessmentCode}/attempts`, {
      method: 'POST',
    })
  }

  async submitAnswer(
    attemptId: string,
    questionId: string,
    selectedOptionId?: string,
    answerText?: string
  ): Promise<{ id: string; is_correct?: boolean; points_awarded?: number }> {
    return this.request(`/attempts/${attemptId}/answers`, {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        selected_option_id: selectedOptionId,
        answer_text: answerText,
      }),
    })
  }

  async submitReasoning(
    answerId: string,
    responseText: string,
    inputMode: string = 'text'
  ): Promise<{
    id: string
    sequence_no: number
    response_text: string
    diagnosis?: DiagnosisResult
  }> {
    return this.request(`/answers/${answerId}/reasoning`, {
      method: 'POST',
      body: JSON.stringify({
        response_text: responseText,
        input_mode: inputMode,
      }),
    })
  }

  async completeAttempt(attemptId: string): Promise<{ id: string; raw_score: number; max_score: number }> {
    return this.request(`/attempts/${attemptId}/complete`, {
      method: 'POST',
    })
  }

  // --- Socratic Tutoring & Practice Diagnostics ---

  async diagnosePractice(
    questionCode: string,
    studentAnswer: string,
    reasoningText?: string,
    inputMode: string = 'text'
  ): Promise<DiagnosisResult & { tutor_prompt?: string; answer_submission_id?: string }> {
    return this.request('/tutoring/practice/diagnose', {
      method: 'POST',
      body: JSON.stringify({
        question_code: questionCode,
        student_answer: studentAnswer,
        reasoning_text: reasoningText,
        input_mode: inputMode,
      }),
    })
  }

  async evaluateTeachBack(explanation: string, inputMode: string = 'text'): Promise<TeachBackEvaluation> {
    return this.request('/tutoring/teach-back/evaluate', {
      method: 'POST',
      body: JSON.stringify({
        explanation,
        input_mode: inputMode,
      }),
    })
  }

  async getTutoringHistory(): Promise<V1TutoringInteraction[]> {
    return this.request<V1TutoringInteraction[]>('/tutoring/history')
  }

  async getMisconceptions(): Promise<V1Misconception[]> {
    return this.request<V1Misconception[]>('/tutoring/misconceptions')
  }

  // --- Progress & Analytics ---

  async getProgress(): Promise<V1ProgressSummary> {
    return this.request<V1ProgressSummary>('/progress/summary')
  }

  // --- ElevenLabs Voice Proxy ---

  async synthesizeVoice(
    text: string,
    interactionId?: string,
    voiceId?: string
  ): Promise<V1VoiceResponse> {
    return this.request<V1VoiceResponse>('/voice/synthesize', {
      method: 'POST',
      body: JSON.stringify({
        text,
        interaction_id: interactionId,
        voice_id: voiceId,
      }),
    })
  }

  async getVoiceEvents(): Promise<V1VoiceEvent[]> {
    return this.request<V1VoiceEvent[]>('/voice/events')
  }
}

export const apiClient = new ApiClient()

