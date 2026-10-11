export type StageKey =
  | 'WELCOME'
  | 'PRE_ASSESSMENT'
  | 'LESSON'
  | 'PRACTICE'
  | 'REMEDIATION'
  | 'TEACH_BACK'
  | 'POST_ASSESSMENT'
  | 'PROGRESS_REPORT'

export interface WorkedExample {
  example_id: string
  prompt: string
  steps: string[]
}

export interface Concept {
  concept_id: string
  title: string
  learning_objectives: string[]
  prerequisites: string[]
  verified_explanation: string
  intuitive_analogy: string
  worked_examples: WorkedExample[]
  common_mistakes: string[]
  source_reference?: string
  question_ids: string[]
  misconception_ids: string[]
}

export interface Chapter {
  chapter_id: string
  title: string
  subject: string
  grade_level: string
  content_version: string
  reviewed_by: string
  reviewed_at: string
  learning_objectives: string[]
  concepts: Concept[]
}

export interface Question {
  question_id: string
  concept_id: string
  content_version: string
  question_text: string
  question_type: string
  difficulty: 'easy' | 'medium' | 'hard'
  options: string[]
  correct_answer?: string // Hidden during pre/post assessment
  verified_explanation?: string // Hidden during pre-assessment
  learning_objective: string
  is_transfer_question: boolean
  misconception_mappings?: Record<string, string>
  remediation_activity_ids: string[]
}

export interface RemediationActivity {
  activity_id: string
  concept_id: string
  title: string
  purpose: string
  instructions: string
  visual_representation?: string
  target_diagnosis_codes: string[]
  question_ids: string[]
  expected_learning_evidence: string
}

export type DiagnosisCode = 'M1' | 'M2' | 'M3' | 'M4' | 'S1' | 'U1' | 'NONE'
export type ReasoningStatus = 'valid' | 'invalid' | 'unclear' | 'not_assessed'
export type Certainty = 'high' | 'medium' | 'low' | 'unknown'

export interface DiagnosisResult {
  question_id: string
  is_correct: boolean
  reasoning_status: ReasoningStatus
  diagnosis_code: DiagnosisCode
  certainty: Certainty
  evidence: string
  clarification_required: boolean
  clarifying_question?: string | null
  next_activity_id?: string | null
  student_feedback: string
}

export type CriterionStatus = 'demonstrated' | 'partial' | 'incorrect' | 'not_demonstrated'

export interface CriterionResult {
  criterion_id: string
  status: CriterionStatus
  evidence: string
}

export interface TeachBackEvaluation {
  rubric_id: string
  content_version: string
  criterion_results: CriterionResult[]
  earned_points: float
  possible_points: float
  coverage_percent: float
  overall_feedback: string
  recommended_concepts: string[]
  clarification_required: boolean
}

type float = number

export interface ConceptScore {
  concept_id: string
  pre_correct: number
  pre_total: number
  post_correct: number
  post_total: number
  pre_percent: number
  post_percent: number
  change_pp: number
}

export interface PrePostReport {
  learner_id: string
  assessment_version: string
  paired_sample_count: number
  pre_correct: number
  pre_total: number
  pre_percent: number
  post_correct: number
  post_total: number
  post_percent: number
  score_change_pp: number
  concept_breakdown: Record<string, ConceptScore>
  limitations: string[]
}

export type MasteryStatus = 'not_assessed' | 'developing' | 'mastered'

export interface ConceptMastery {
  concept_id: string
  status: MasteryStatus
  score: number
  evidence_attempt_count: number
  distinct_question_count: number
  transfer_passed: boolean
}

export interface ReviewTask {
  id: string
  learner_id: string
  concept_id: string
  reason: string
  due_at: string
  status: 'due' | 'completed'
}

// API v1 Types
export interface V1Session {
  id: string
  token?: string
  stage: string
  created_at?: string
  expires_at?: string
}

export interface V1LessonConcept {
  id: string
  code: string
  name: string
  description?: string
}

export interface V1Lesson {
  id: string
  code: string
  title: string
  sequence_no: number
  description?: string
  concepts?: V1LessonConcept[]
}

export interface V1Option {
  id: string
  option_key: string
  option_text: string
}

export interface V1Question {
  id: string
  code?: string
  prompt: string
  question_type: string
  options: V1Option[]
}

export interface V1Assessment {
  id: string
  code: string
  title: string
  assessment_type: string
  version: number
  questions: V1Question[]
}

export interface V1Attempt {
  id: string
  assessment_id: string
  attempt_no: number
  status: string
  raw_score?: number
  max_score?: number
}

export interface V1ProgressConcept {
  concept_code: string
  name: string
  status: string
}

export interface V1ProgressSummary {
  session_id: string
  current_stage: string
  pre_assessment_score: number | null
  post_assessment_score: number | null
  growth_delta: number | null
  concepts: V1ProgressConcept[]
}

export interface V1VoiceResponse {
  status: 'succeeded' | 'fallback'
  audio_base64: string | null
  mime_type: string | null
  duration_ms: number
  fallback_text: string
  message: string
  voice_event_id: string
}

export interface V1VoiceTranscribeResponse {
  status: 'succeeded' | 'failed' | 'fallback'
  text: string
  duration_ms: number
  message: string
  voice_event_id: string
}

export interface V1VoiceEvent {
  id: string
  status: string
  direction: string
  duration_ms: number | null
  error_code: string | null
  created_at: string
}

export interface V1TutoringInteraction {
  id: string
  sequence_no: number
  role: 'student' | 'tutor' | 'system'
  interaction_type: string
  content: string
  created_at: string
}

export interface V1Misconception {
  id: string
  code: string
  concept_code: string | null
  description: string
  confidence: number | null
  status: string
  evidence_answer_id?: string | null
  created_at: string
  updated_at?: string | null
}
