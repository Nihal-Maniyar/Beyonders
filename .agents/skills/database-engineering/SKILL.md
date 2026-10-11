---
name: database-engineering
description: >-
  Use this skill when defining, auditing, or modifying LearnLoop AI relational schemas,
  SQLAlchemy 2 models, seed scripts, transaction boundaries, or database migrations.
---

# Database Engineering Workflow for LearnLoop AI

This skill provides step-by-step procedures for managing the 15 relational entities of LearnLoop AI, ensuring cross-dialect compatibility (SQLite and PostgreSQL), strict relational integrity, and safe seed operations.

## Relational Entity Model

Ensure all models in `src/learnloop/db/models.py` conform to the 15 entities defined in `context.md` Section 16–20:
1. `learning_sessions`: anonymous session tracking and expiry
2. `concepts`: fraction concept registry (`C1`, `C2`, `C3`)
3. `lessons`: instructional unit content
4. `lesson_concepts`: composite junction `(lesson_id, concept_id)`
5. `questions`: assessment & practice questions
6. `question_options`: choices with hidden correctness flags (`is_correct`)
7. `question_concepts`: composite junction `(question_id, concept_id)`
8. `assessments`: versioned assessment definitions (`pre`, `post`, `practice`)
9. `assessment_questions`: ordered question membership with `points_possible`
10. `assessment_attempts`: session attempt tracking with `raw_score` & `max_score`
11. `answer_submissions`: submitted answers with points awarded
12. `reasoning_responses`: student explanations linked to answers
13. `tutoring_interactions`: conversation & feedback event log
14. `misconception_hypotheses`: detected misconceptions with confidence and lifecycle status
15. `voice_events`: ElevenLabs telemetry and audit log

## Dialect Compatibility Rules

- Use `String(36)` columns with default UUID generators so models run cleanly on SQLite (for quick local development and pytest) and PostgreSQL (for deployment).
- Enforce foreign keys with `ondelete="RESTRICT"` for historical student attempts and answers to prevent accidental cascading deletion.
- Content junction tables (`lesson_concepts`, `question_concepts`) may use `ondelete="CASCADE"` for draft cleanups.

## Step-by-Step Procedures

### 1. Model Definition & Migration Validation
1. Verify declarative mappings inherit from `Base` (`DeclarativeBase`).
2. Verify explicit unique and index constraints:
   - Unique: `(session_id, assessment_id, attempt_no)` on `assessment_attempts`
   - Unique: `(attempt_id, question_id)` on `answer_submissions`
   - Unique: `(answer_submission_id, sequence_no)` on `reasoning_responses`
   - Index: `idx_sessions_expiry` on `learning_sessions.expires_at`
   - Index: `idx_attempts_session_started` on `assessment_attempts (session_id, started_at DESC)`

### 2. Idempotent Database Seeding
1. Execute `src/learnloop/db/seed.py`:
   - Populates concepts `C1` (equal parts / unit fractions), `C2` (comparing fractions), `C3` (equivalent fractions).
   - Populates pre-assessment, post-assessment, and practice questions from verified content bank.
   - Idempotently skips existing records based on unique codes.
2. Verify seed execution:
   ```bash
   python -c "from learnloop.db.session import init_db; from learnloop.db.seed import seed_database; init_db(); seed_database()"
   ```

### 3. Transaction Safety Verification
- When scoring an attempt, wrap answer calculation, attempt status transition (`in_progress` -> `completed`), and score commits in a single database transaction.
- Roll back immediately if any constraint or validation fails.

