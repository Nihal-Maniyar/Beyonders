# LearnLoop AI — Database Documentation

**Document version:** 1.0  
**Status:** Implemented (Phase 1)  
**ORM:** SQLAlchemy 2.x  
**Dialect Compatibility:** SQLite (local development and automated testing) & PostgreSQL (deployed target)  

---

## 1. Overview
The LearnLoop AI database architecture implements the 15 relational entities specified in `context.md` Section 16–20. It models anonymous learning sessions, fraction curriculum concepts, instructional lessons, assessment definitions, student attempts, answer submissions, reasoning responses, tutoring interactions, misconception hypotheses, and voice provider telemetry.

To guarantee zero regression for the live demo backup, legacy tables (`learners`, `attempts`, `assessment_runs`, etc.) are preserved in `src/learnloop/db/models.py` for direct execution of `app.py`.

---

## 2. Table Specifications

### 2.1 Core Learning Entities

#### `learning_sessions`
Tracks anonymous student session state and validity.
- `id` (VARCHAR(36), PK): UUID string.
- `token_hash` (VARCHAR(128), UNIQUE, INDEX): HMAC-SHA256 hash of the secret session token.
- `status` (VARCHAR(20), NOT NULL): Session state (`active`, `completed`, `expired`).
- `created_at` (TIMESTAMP): UTC creation timestamp.
- `updated_at` (TIMESTAMP): UTC update timestamp.
- `expires_at` (TIMESTAMP, NOT NULL, INDEX): Expiry deadline.
- `completed_at` (TIMESTAMP, NULL): Completion timestamp.

#### `concepts`
Registry of fraction concepts.
- `id` (VARCHAR(36), PK): UUID string.
- `code` (VARCHAR(20), UNIQUE, INDEX): Concept code (`C1`, `C2`, `C3`).
- `name` (VARCHAR(200), NOT NULL): Concept name.
- `description` (TEXT, NULL): Pedagogical description.
- `created_at` (TIMESTAMP): UTC creation timestamp.

#### `lessons`
Instructional fraction lessons.
- `id` (VARCHAR(36), PK): UUID string.
- `code` (VARCHAR(50), UNIQUE, INDEX): Lesson identifier.
- `title` (VARCHAR(255), NOT NULL): Lesson title.
- `content` (TEXT, NOT NULL): Lesson explanation text.
- `status` (VARCHAR(20), NOT NULL): Content status (`draft`, `published`, `archived`).
- `sequence_no` (INTEGER, NOT NULL): Ordering index.
- `created_at` (TIMESTAMP), `updated_at` (TIMESTAMP).

#### `lesson_concepts`
Junction mapping lessons to covered concepts.
- `lesson_id` (VARCHAR(36), FK `lessons.id`, ON DELETE CASCADE, PK).
- `concept_id` (VARCHAR(36), FK `concepts.id`, ON DELETE RESTRICT, PK).

---

### 2.2 Assessment & Question Entities

#### `questions`
Assessment, practice, and transfer questions.
- `id` (VARCHAR(36), PK): UUID string.
- `code` (VARCHAR(50), UNIQUE, INDEX): Stable question code (e.g., `Q_C1_PRE_01`).
- `prompt` (TEXT, NOT NULL): Question prompt text.
- `question_type` (VARCHAR(30), NOT NULL): `multiple_choice` or `short_text`.
- `status` (VARCHAR(20), NOT NULL): `draft`, `published`, `archived`.
- `explanation` (TEXT, NULL): Verified mathematical explanation.
- `created_at` (TIMESTAMP), `updated_at` (TIMESTAMP).

#### `question_options`
Multiple-choice options.
- `id` (VARCHAR(36), PK): UUID string.
- `question_id` (VARCHAR(36), FK `questions.id`, ON DELETE CASCADE, INDEX).
- `option_key` (VARCHAR(10), NOT NULL): Option identifier (`A`, `B`, `C`, `D`).
- `option_text` (TEXT, NOT NULL): Option text.
- `is_correct` (BOOLEAN, NOT NULL): Internal correctness flag. Never sent in public assessment payloads.
- **Constraint:** `UNIQUE (question_id, option_key)`.

#### `question_concepts`
Junction mapping questions to tested concepts.
- `question_id` (VARCHAR(36), FK `questions.id`, ON DELETE CASCADE, PK).
- `concept_id` (VARCHAR(36), FK `concepts.id`, ON DELETE RESTRICT, PK).

#### `assessments`
Versioned assessments (`pre`, `post`, `practice`).
- `id` (VARCHAR(36), PK): UUID string.
- `code` (VARCHAR(50), NOT NULL, INDEX): Assessment code (e.g., `FRACTIONS_PRE`).
- `title` (VARCHAR(255), NOT NULL): Display title.
- `assessment_type` (VARCHAR(20), NOT NULL): `pre`, `post`, `practice`.
- `version` (INTEGER, NOT NULL, DEFAULT 1).
- `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE).
- `created_at` (TIMESTAMP).
- **Constraint:** `UNIQUE (code, version)`.

#### `assessment_questions`
Ordered questions within an assessment version.
- `assessment_id` (VARCHAR(36), FK `assessments.id`, ON DELETE RESTRICT, PK).
- `question_id` (VARCHAR(36), FK `questions.id`, ON DELETE RESTRICT, PK).
- `position` (INTEGER, NOT NULL): 1-indexed order.
- `points_possible` (FLOAT, NOT NULL, DEFAULT 1.0).
- **Constraint:** `UNIQUE (assessment_id, position)`.

---

### 2.3 Attempt & Tutoring Entities

#### `assessment_attempts`
Student attempts at completing an assessment.
- `id` (VARCHAR(36), PK): UUID string.
- `session_id` (VARCHAR(36), FK `learning_sessions.id`, ON DELETE RESTRICT, INDEX).
- `assessment_id` (VARCHAR(36), FK `assessments.id`, ON DELETE RESTRICT, INDEX).
- `attempt_no` (INTEGER, NOT NULL, DEFAULT 1).
- `status` (VARCHAR(20), NOT NULL): `in_progress`, `completed`, `abandoned`.
- `raw_score` (FLOAT, NULL), `max_score` (FLOAT, NULL).
- `started_at` (TIMESTAMP), `completed_at` (TIMESTAMP, NULL).
- **Constraint:** `UNIQUE (session_id, assessment_id, attempt_no)`.

#### `answer_submissions`
Individual submitted answers per attempt.
- `id` (VARCHAR(36), PK): UUID string.
- `attempt_id` (VARCHAR(36), FK `assessment_attempts.id`, ON DELETE RESTRICT, INDEX).
- `question_id` (VARCHAR(36), FK `questions.id`, ON DELETE RESTRICT, INDEX).
- `selected_option_id` (VARCHAR(36), FK `question_options.id`, ON DELETE RESTRICT, NULL).
- `answer_text` (TEXT, NULL).
- `is_correct` (BOOLEAN, NULL).
- `points_awarded` (FLOAT, NULL).
- `submitted_at` (TIMESTAMP).
- **Constraint:** `UNIQUE (attempt_id, question_id)`.

#### `reasoning_responses`
Student explanations linked to submitted answers.
- `id` (VARCHAR(36), PK): UUID string.
- `answer_submission_id` (VARCHAR(36), FK `answer_submissions.id`, ON DELETE RESTRICT, INDEX).
- `sequence_no` (INTEGER, NOT NULL, DEFAULT 1).
- `response_text` (TEXT, NOT NULL).
- `input_mode` (VARCHAR(30), NOT NULL): `text` or `speech_transcript`.
- `created_at` (TIMESTAMP).
- **Constraint:** `UNIQUE (answer_submission_id, sequence_no)`.

#### `tutoring_interactions`
Log of conversational tutoring turns.
- `id` (VARCHAR(36), PK): UUID string.
- `session_id` (VARCHAR(36), FK `learning_sessions.id`, ON DELETE RESTRICT, INDEX).
- `sequence_no` (INTEGER, NOT NULL): 1-indexed dialogue step.
- `role` (VARCHAR(20), NOT NULL): `student`, `tutor`, `system`.
- `interaction_type` (VARCHAR(50), NOT NULL): `explanation`, `question`, `feedback`, `teach_back`, etc.
- `content` (TEXT, NOT NULL).
- `created_at` (TIMESTAMP).
- **Constraint:** `UNIQUE (session_id, sequence_no)`.

#### `misconception_hypotheses`
Diagnosed misconceptions and confidence tracking.
- `id` (VARCHAR(36), PK): UUID string.
- `session_id` (VARCHAR(36), FK `learning_sessions.id`, ON DELETE RESTRICT, INDEX).
- `concept_id` (VARCHAR(36), FK `concepts.id`, ON DELETE RESTRICT, NULL).
- `evidence_answer_id` (VARCHAR(36), FK `answer_submissions.id`, ON DELETE RESTRICT, NULL).
- `code` (VARCHAR(20), NOT NULL): `M1`, `M2`, `M3`, `M4`, `S1`, `U1`, `NONE`.
- `description` (TEXT, NOT NULL).
- `confidence` (FLOAT, NULL): Value between 0.0 and 1.0.
- `status` (VARCHAR(20), NOT NULL): `tentative`, `confirmed`, `resolved`, `rejected`.
- `created_at` (TIMESTAMP), `updated_at` (TIMESTAMP).

#### `voice_events`
Operational audit log for ElevenLabs voice requests.
- `id` (VARCHAR(36), PK): UUID string.
- `session_id` (VARCHAR(36), FK `learning_sessions.id`, ON DELETE RESTRICT, INDEX).
- `interaction_id` (VARCHAR(36), FK `tutoring_interactions.id`, ON DELETE SET NULL, NULL).
- `provider` (VARCHAR(50), NOT NULL, DEFAULT 'elevenlabs').
- `direction` (VARCHAR(30), NOT NULL): `text_to_speech` or `speech_to_text`.
- `status` (VARCHAR(20), NOT NULL): `requested`, `succeeded`, `failed`, `cancelled`.
- `duration_ms` (INTEGER, NULL): Latency in milliseconds.
- `error_code` (VARCHAR(100), NULL).
- `created_at` (TIMESTAMP).

---

## 3. Seeding Workflow
Database seeding is managed by `src/learnloop/db/seed.py`:
- Populates concepts `C1`, `C2`, `C3` from `data/fractions_chapter.json`.
- Populates instructional lessons mapped to each concept.
- Populates all questions and options from `data/questions.json`.
- Configures default assessments (`FRACTIONS_PRE`, `FRACTIONS_POST`, `FRACTIONS_PRACTICE`).
- **Idempotency:** Re-executing `seed_database()` detects existing records by unique code and will not duplicate records.

