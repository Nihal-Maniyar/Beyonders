# LearnLoop AI — REST API v1 Specification

> **Version:** 1.0.0  
> **Base Path:** `/api/v1`  
> **Source of Truth:** [`context.md`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/context.md)  
> **Authentication:** Anonymous Session Token (HMAC-SHA256 verified)

---

## 1. Architectural Principles & Security Contract

### 1.1 Anonymous Session Isolation
LearnLoop AI requires zero persistent learner accounts or passwords. Learners authenticate via high-entropy, cryptographically random secret tokens (`ll_sec_...`).
- **Token Separation:** The secret token is returned exactly once during session initialization (`POST /api/v1/sessions`).
- **Database Hashing:** The database stores only a salted HMAC-SHA256 hash (`token_hash`) inside the `learning_sessions` entity. The plaintext secret token is never persisted.
- **Client Transmission:** Clients authenticate using either:
  1. `Authorization: Bearer <secret_token>`
  2. `X-Session-Token: <secret_token>` header
  3. `learnloop_session=<secret_token>` HTTP-only cookie
- **Cross-Learner Isolation:** All attempt, submission, and interaction records are strictly scoped to the authenticated session's `session_id`. Any attempt to read or mutate another session's data returns `403 Forbidden` or `404 Not Found`.

### 1.2 Question Confidentiality Guarantee
To preserve pedagogical validity and prevent cheating or client-side leakage:
- Assessment question prompts and options served via `GET /api/v1/assessments/{code}` **never** include `is_correct`, explanations, or answer keys.
- Scoring and diagnosis rules are executed purely server-side upon attempt completion.

### 1.3 Uniform Error Envelope
All error responses (4xx and 5xx) strictly follow the standardized envelope:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource could not be found.",
    "details": []
  }
}
```

---

## 2. API Endpoints

### 2.1 Session Management

#### `POST /api/v1/sessions`
Initializes a new anonymous learning session.
- **Request Body:**
  ```json
  {
    "grade_level": 4,
    "preferences": {}
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "session_id": "e7b0fa45-...",
    "session_token": "ll_sec_...",
    "stage": "pre_assessment",
    "created_at": "2026-10-11T13:20:00Z",
    "expires_at": "2026-10-12T13:20:00Z"
  }
  ```
- **Cookies:** Sets `learnloop_session` with `httponly=True`, `samesite="lax"`.

#### `GET /api/v1/sessions/current`
Retrieves metadata and current stage for the authenticated session.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`200 OK`):**
  ```json
  {
    "id": "e7b0fa45-...",
    "stage": "pre_assessment",
    "created_at": "2026-10-11T13:20:00Z",
    "last_active_at": "2026-10-11T13:25:00Z",
    "expires_at": "2026-10-12T13:20:00Z",
    "metadata": {"grade_level": 4}
  }
  ```

#### `DELETE /api/v1/sessions/current`
Terminates and invalidates the session token immediately.
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "message": "Session successfully invalidated."
  }
  ```

---

### 2.2 Lessons & Curriculum

#### `GET /api/v1/lessons`
Lists all available curriculum lessons in pedagogical order.
- **Authentication:** Public or Session-authenticated.
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": "b3f...",
      "code": "FRACTIONS_FOUNDATION",
      "title": "Understanding Fractions: Parts of a Whole",
      "description": "Learn equal parts, numerators, and denominators.",
      "sequence_order": 1,
      "concepts": [
        {"code": "C1", "name": "Equal parts of a whole"},
        {"code": "C2", "name": "Numerator vs denominator roles"}
      ]
    }
  ]
  ```

#### `GET /api/v1/lessons/{code}`
Retrieves detailed information and associated learning concepts for a specific lesson.
- **Response (`200 OK`):** Single lesson object as above.
- **Errors:** `404 Not Found` if lesson code does not exist.

---

### 2.3 Diagnostic Assessments

#### `GET /api/v1/assessments/{code}`
Retrieves the safe question definitions for an assessment (`FRACTIONS_PRE` or `FRACTIONS_POST`).
- **Response (`200 OK`):**
  ```json
  {
    "assessment_code": "FRACTIONS_PRE",
    "title": "Fractions Pre-Assessment",
    "type": "pre",
    "total_questions": 6,
    "questions": [
      {
        "id": "q-123...",
        "question_code": "Q_C1_PRE_01",
        "prompt": "Which shape shows 1/4 shaded?",
        "question_type": "multiple_choice",
        "difficulty": 1,
        "options": [
          {"id": "opt-1", "label": "A", "text": "Square split into 4 equal quarters", "sequence_order": 1},
          {"id": "opt-2", "label": "B", "text": "Square split into 3 unequal strips", "sequence_order": 2}
        ]
      }
    ]
  }
  ```
  *(Notice: `is_correct` and answer keys are never revealed).*

#### `POST /api/v1/assessments/{code}/attempts`
Starts a new assessment attempt or returns an existing in-progress attempt for the active session.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`201 Created`):**
  ```json
  {
    "attempt_id": "att-456...",
    "session_id": "e7b0fa45-...",
    "assessment_code": "FRACTIONS_PRE",
    "status": "in_progress",
    "started_at": "2026-10-11T13:21:00Z"
  }
  ```

#### `GET /api/v1/assessments/attempts/{attempt_id}`
Returns current submission status for the attempt.
- **Response (`200 OK`):**
  ```json
  {
    "attempt_id": "att-456...",
    "session_id": "e7b0fa45-...",
    "assessment_code": "FRACTIONS_PRE",
    "status": "in_progress",
    "started_at": "2026-10-11T13:21:00Z",
    "answered_count": 2,
    "total_questions": 6,
    "submissions": [
      {"question_code": "Q_C1_PRE_01", "selected_option_id": "opt-1"}
    ]
  }
  ```

#### `POST /api/v1/assessments/attempts/{attempt_id}/answers`
Idempotently records an answer choice for a question.
- **Request Body:**
  ```json
  {
    "question_code": "Q_C1_PRE_01",
    "selected_option_id": "opt-1",
    "raw_answer": "A"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "question_code": "Q_C1_PRE_01",
    "answered_count": 1,
    "total_questions": 6
  }
  ```

#### `POST /api/v1/assessments/attempts/{attempt_id}/complete`
Concludes the assessment attempt, computes deterministic scoring, updates session stage, and generates diagnostic summaries.
- **Preconditions:** All questions must be answered (`400 Bad Request` if unanswered questions remain).
- **Idempotency:** Calling `complete` on an already completed attempt returns the existing score without double-counting.
- **Response (`200 OK`):**
  ```json
  {
    "attempt_id": "att-456...",
    "status": "completed",
    "score": 83.3,
    "completed_at": "2026-10-11T13:25:00Z",
    "results": [
      {
        "question_code": "Q_C1_PRE_01",
        "is_correct": true,
        "selected_option_id": "opt-1",
        "explanation": "Correct! The shape has 4 equal parts with 1 shaded."
      }
    ]
  }
  ```

---

### 2.4 Progress & Learning Metrics

#### `GET /api/v1/progress/summary`
Calculates comprehensive learner progress across both assessments, concept mastery states, and learning growth.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`200 OK`):**
  ```json
  {
    "session_id": "e7b0fa45-...",
    "current_stage": "completed",
    "pre_assessment_score": 50.0,
    "post_assessment_score": 100.0,
    "growth_delta": 50.0,
    "concepts": [
      {
        "concept_code": "C1",
        "name": "Equal parts of a whole",
        "status": "mastered"
      },
      {
        "concept_code": "C2",
        "name": "Numerator vs denominator roles",
        "status": "mastered"
      }
    ]
  }
  ```

---

### 2.5 Socratic Tutoring & Diagnostics

#### `POST /api/v1/answers/{answer_id}/reasoning`
Submits student reasoning for a previously recorded answer submission within an attempt.
- **Headers:** `Authorization: Bearer <session_token>`
- **Request Body:**
  ```json
  {
    "response_text": "Because it has 4 equal pieces and 1 is shaded.",
    "input_mode": "text"
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "id": "res-uuid...",
    "answer_submission_id": "ans-uuid...",
    "sequence_no": 1,
    "response_text": "Because it has 4 equal pieces and 1 is shaded.",
    "input_mode": "text",
    "created_at": "2026-10-11T13:45:00Z",
    "diagnosis": {
      "question_id": "Q_C1_PRE_01",
      "is_correct": true,
      "diagnosis_code": "NONE"
    }
  }
  ```

#### `POST /api/v1/tutoring/practice/diagnose` *(alias `POST /api/v1/tutor/messages`)*
Diagnoses a practice question choice and student explanation using deterministic rules (M1–M4, S1, U1). Persists reasoning responses, updates tentative misconception hypotheses, and logs student/tutor dialogue turns.
- **Headers:** `Authorization: Bearer <session_token>`
- **Request Body:**
  ```json
  {
    "question_code": "Q_C2_PRE_01",
    "student_answer": "A",
    "reasoning_text": "2/5 is larger because five is bigger than three.",
    "input_mode": "text"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "question_id": "Q_C2_PRE_01",
    "is_correct": false,
    "diagnosis_code": "M1",
    "reasoning_status": "invalid",
    "certainty": "high",
    "evidence": "Student compared denominators using whole-number magnitudes...",
    "clarification_required": false,
    "clarifying_question": null,
    "next_activity_id": "A_FRACTION_STRIPS",
    "student_feedback": "It looks like you might be thinking of denominators like regular whole numbers...",
    "tutor_prompt": "It looks like you might be thinking of denominators like regular whole numbers..."
  }
  ```

#### `POST /api/v1/tutoring/teach-back/evaluate` *(alias `POST /api/v1/tutor/teach-back`)*
Evaluates learner explanations against the 5-point rubric (R1–R5: numerator/denominator roles, equal-sized parts, part size vs part count, comparison methods, equivalent fractions).
- **Headers:** `Authorization: Bearer <session_token>`
- **Request Body:**
  ```json
  {
    "explanation": "The denominator tells the total number of equal parts in a whole, and numerator counts the pieces. All parts must be equal-sized fair shares..."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "rubric_id": "RUBRIC_FRACTIONS_01",
    "content_version": "fractions-v1.0",
    "earned_points": 5.0,
    "possible_points": 5.0,
    "coverage_percent": 100.0,
    "overall_feedback": "Outstanding explanation! You clearly demonstrated all key fraction concepts.",
    "criterion_results": [
      {"criterion_id": "R1", "status": "demonstrated", "evidence": "..."},
      {"criterion_id": "R2", "status": "demonstrated", "evidence": "..."}
    ],
    "recommended_concepts": [],
    "clarification_required": false
  }
  ```

#### `GET /api/v1/tutoring/history` *(alias `GET /api/v1/tutor/history`)*
Retrieves ordered dialogue turns between learner and tutor for the current session.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": "int-1",
      "sequence_no": 1,
      "role": "student",
      "interaction_type": "reasoning_response",
      "content": "Answer: A. Reasoning: 2/5 is larger...",
      "created_at": "2026-10-11T13:40:00Z"
    },
    {
      "id": "int-2",
      "sequence_no": 2,
      "role": "tutor",
      "interaction_type": "practice_feedback",
      "content": "It looks like you might be thinking...",
      "created_at": "2026-10-11T13:40:01Z"
    }
  ]
  ```

#### `GET /api/v1/tutoring/misconceptions` *(alias `GET /api/v1/tutor/misconceptions`)*
Retrieves all recorded misconception hypotheses for the authenticated learner session.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": "hyp-1",
      "code": "M1",
      "concept_code": "C2",
      "description": "It looks like you might be thinking of denominators like regular whole numbers...",
      "confidence": 0.9,
      "status": "tentative",
      "evidence_answer_id": "ans-uuid...",
      "created_at": "2026-10-11T13:40:00Z",
      "updated_at": "2026-10-11T13:40:00Z"
    }
  ]
  ```

---

### 2.6 ElevenLabs Voice Integration & Operational Telemetry

#### `POST /api/v1/voice/synthesize`
Synthesizes spoken tutor output using ElevenLabs via server-side proxy.
- **Security:** Backend proxy hides all provider API keys.
- **Timeout Bound:** Strict maximum 5.0 seconds.
- **Fallback Guarantee:** Never crashes the learning flow. If unconfigured, timed out, or quota exhausted, returns `status: "fallback"` with full tutor text.
- **Headers:** `Authorization: Bearer <session_token>`
- **Request Body:**
  ```json
  {
    "text": "Let's explore fraction strips together to see why 2/3 is bigger than 2/5.",
    "interaction_id": "optional-interaction-uuid"
  }
  ```
- **Response (`200 OK` - Success):**
  ```json
  {
    "status": "succeeded",
    "audio_base64": "UklGRi...",
    "mime_type": "audio/mpeg",
    "duration_ms": 782,
    "fallback_text": "Let's explore fraction strips together...",
    "message": "Speech synthesized successfully.",
    "voice_event_id": "ve-uuid..."
  }
  ```
- **Response (`200 OK` - Fallback Mode):**
  ```json
  {
    "status": "fallback",
    "audio_base64": null,
    "mime_type": null,
    "duration_ms": 0,
    "fallback_text": "Let's explore fraction strips together...",
    "message": "Voice synthesis unavailable: no ElevenLabs API key configured. Displaying tutor text.",
    "voice_event_id": "ve-uuid..."
  }
  ```

#### `GET /api/v1/voice/events`
Returns operational telemetry and audit logs for voice synthesis requests under the authenticated session.
- **Headers:** `Authorization: Bearer <session_token>`
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": "ve-uuid...",
      "status": "failed",
      "direction": "text_to_speech",
      "duration_ms": 0,
      "error_code": "VOICE_CREDENTIALS_MISSING",
      "created_at": "2026-10-11T13:48:00Z"
    }
  ]
  ```

---

## 3. Legacy Route Compatibility
The original `/api` endpoints continue to be available alongside `/api/v1` to guarantee total backward compatibility with the independent Streamlit application (`app.py`).
- `GET /api/health`
- `POST /api/sessions`
- `GET /api/content/syllabus`
- `GET /api/assessments/fixed-benchmark`
- `POST /api/tutoring/diagnose-practice`
- `POST /api/tutoring/evaluate-teachback`
