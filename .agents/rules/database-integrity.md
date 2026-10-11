# Database Integrity Rules

## 1. Schema Definition & Entities
- Model the 15 relational entities specified in `context.md` Section 16–20 using SQLAlchemy 2 DeclarativeBase.
- Table names must strictly match:
  1. `learning_sessions`
  2. `concepts`
  3. `lessons`
  4. `lesson_concepts`
  5. `questions`
  6. `question_options`
  7. `question_concepts`
  8. `assessments`
  9. `assessment_questions`
  10. `assessment_attempts`
  11. `answer_submissions`
  12. `reasoning_responses`
  13. `tutoring_interactions`
  14. `misconception_hypotheses`
  15. `voice_events`

## 2. Dialect and Key Constraints
- Dual-dialect compatibility: Use `String(36)` / `UUID` compatibility so models work seamlessly on SQLite (local development and pytest in-memory) and PostgreSQL (production deployment).
- Primary keys must be UUIDs generated on the server or database.
- Enforce unique composite constraints:
  - `assessment_questions`: `(assessment_id, position)`
  - `assessment_attempts`: `(session_id, assessment_id, attempt_no)`
  - `answer_submissions`: `(attempt_id, question_id)`
  - `reasoning_responses`: `(answer_submission_id, sequence_no)`
  - `tutoring_interactions`: `(session_id, sequence_no)`

## 3. Transaction Safety & Idempotency
- All state-altering operations (submitting an answer, completing an attempt, logging a misconception hypothesis) must execute inside an explicit database transaction (`session.commit()` with rollback on failure).
- Attempt completion must verify that all required assessment questions have answers before finalizing.
- Duplicate submission handling:
  - Repeated calls to complete an already completed attempt must return the existing completed attempt or HTTP 409, without mutating timestamps or recalculating scores.
  - Submitting an answer for an already completed attempt must be rejected with HTTP 409 or HTTP 400.

## 4. Deletion & Data Retention
- Never cascade-delete historical attempts, submitted answers, or reasoning responses when a session expires.
- Expired sessions transition status (`status = 'expired'`).
- Do not store binary audio data in the database; `voice_events` stores operational telemetry and duration only.

