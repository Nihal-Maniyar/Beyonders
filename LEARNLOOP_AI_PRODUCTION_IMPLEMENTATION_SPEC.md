# LearnLoop AI --- Production Implementation Specification

**Product:** LearnLoop AI --- Adaptive AI Tutor & Misconception
Detector\
**Hackathon:** VORTEXA 3.0 · **Problem statement:** E-01 · **Domain:**
AI-Powered Education & Learning Technology\
**Status:** Implementation contract for an AI coding agent\
**Primary stack:** Python, Streamlit, SQLAlchemy, SQLite for local
development, PostgreSQL for persistent deployment, JSON content bank,
optional LLM adapter, optional ElevenLabs voice services.

------------------------------------------------------------------------

## 0. Instructions to the implementing agent

You are the technical architect and implementation agent for an existing
project. Treat this document as the target specification, not evidence
that features already exist.

1.  Inspect the repository and `context.md` first. Read the existing
    README, dependency files, source code, tests, Git status, branches,
    and remote configuration before changing anything.
2.  Preserve working implementation. Do not replace the project
    wholesale or change the stack without a concrete reason.
3.  Create a short implementation audit: working, partial, missing,
    broken, and untested. Then implement the highest-priority missing
    end-to-end behavior.
4.  Keep mathematical answer checking, answer keys, score calculations,
    and mastery calculations deterministic. Use an LLM only for
    constrained language interpretation and grounded feedback.
5.  Do not fabricate attempts, mastery, assessment results, provider
    responses, or successful tests.
6.  Never expose secrets in source code, browser code, logs,
    screenshots, commits, or documentation.
7.  Add and run tests at each meaningful checkpoint. Finish with an
    end-to-end test and a deployment smoke test.
8.  Make small, coherent Git commits. Push to the configured GitHub
    remote when credentials and permissions are available. Never
    force-push, rewrite shared history, or commit secrets. If pushing is
    blocked, report the exact blocker and leave the local branch and
    commits intact.
9.  Follow the supplied Anthropic frontend-design skill principles: plan
    the product-specific visual direction before styling, use a cohesive
    design system, avoid generic AI-generated aesthetics, and make every
    interface state purposeful. Do not blindly install external skills
    or execute unreviewed scripts; inspect their source and license
    first.
10. Do not claim production readiness until the relevant acceptance
    criteria in this document have been tested. Separate "implemented",
    "tested", and "not verified" in the final report.

### First action: repository audit

Run and inspect equivalents of:

``` bash
pwd
git status --short --branch
git remote -v
git log -5 --oneline
find . -maxdepth 3 -type f \
  -not -path './.git/*' -not -path './.venv/*' | sort
```

Read `context.md`, `README.md`, `pyproject.toml` or `requirements.txt`,
`.gitignore`, all application modules, tests, deployment configuration,
and any database schema/migrations. Do not print `.env`, Streamlit
secrets, tokens, or credentials. If `context.md` is missing, use this
specification and report that it was missing; do not invent its
contents.

------------------------------------------------------------------------

## 1. Product definition

LearnLoop AI is an evidence-driven tutor for one initial chapter:
**comparing fractions**. It teaches from approved material, asks
students to explain incorrect answers, identifies a likely misconception
only when evidence supports it, adapts remediation, evaluates student
teach-back against a rubric, and tracks demonstrated learning over time.

The core differentiator is not voice or generic chat. It is this loop:

``` text
Approved content
  → baseline assessment
  → teach a concept
  → answer + reasoning
  → diagnose or ask for clarification
  → targeted activity
  → new evidence
  → student teach-back
  → rubric evaluation
  → targeted revision
  → same-item post-assessment
  → evidence-based progress report
```

The tutor supports teachers; it does not replace them. Teacher-approved
content is the source of truth for scored educational content.

### Product principles

-   Evidence before diagnosis.
-   Correctness and reasoning are stored separately.
-   "Not demonstrated" is not the same as "misunderstood."
-   AI outputs are untrusted until schema-validated and checked against
    approved IDs.
-   A missing AI/voice provider must not break the core learning flow.
-   Every displayed metric must be derived from persisted records or
    explicitly labelled sample data.
-   The system must communicate uncertainty in plain language.
-   The app should be usable by a beginner student without technical
    terminology.

------------------------------------------------------------------------

## 2. Scope and priorities

### P0 --- required complete learning loop

-   Prepared, teacher-reviewable fractions syllabus.
-   Six fixed pre-assessment items: two for each of three concepts.
-   One-question-at-a-time assessment UX; persist each answer.
-   Verified answer checking.
-   Misconception classification, including insufficient evidence and
    clarification.
-   Different supported misconceptions produce different activities.
-   Approved lessons, examples, practice, and targeted remediation.
-   Text teach-back and rubric-based evaluation.
-   Persistent attempts and assessment records.
-   Concept-level mastery derived from saved evidence.
-   Same six fixed questions for post-assessment.
-   Report pre/post score, percentage-point change, paired sample count,
    concept results, and limitations.
-   Error handling, tests, accessibility basics, and clear setup
    instructions.

### P1 --- voice, only after P0 is stable

-   ElevenLabs text-to-speech for approved explanations/feedback.
-   Speech-to-text for quiz answers and teach-back, using a separately
    verified transcription provider or supported browser capability.
-   Visible microphone state, stop control, editable transcript,
    permission handling, and text fallback.
-   Never assume ElevenLabs TTS automatically provides speech
    recognition.

### P2 --- lightweight review and progress UX

-   Persist a next-review date and reason for review.
-   A "Due for review" panel querying saved tasks.
-   Basic progress dashboard based on real records.

### Explicitly out of scope unless separately approved

Multi-subject or multi-grade support; arbitrary PDF ingestion; full
teacher portal and classroom accounts; multi-student analytics;
push/email notifications; background job infrastructure; advanced spaced
repetition; custom-trained models; knowledge graphs; LMS integrations;
mobile apps; leaderboards; parental dashboards; fine-tuning; real-time
autonomous voice with interruption handling; complex microservices;
Kubernetes; and production-scale observability infrastructure.

Do not begin P1 or P2 until the P0 acceptance tests pass.

------------------------------------------------------------------------

## 3. Recommended architecture

Use a modular monolith. Streamlit is the UI layer, but business logic
must not live inside UI event handlers. Keep interfaces clean so a
separate API can be added later without rewriting the educational
engine.

``` text
Browser
  │
  ▼
Streamlit UI / pages
  │ calls application use-cases
  ▼
Application services / learning controller
  ├── AssessmentService
  ├── TutorService
  ├── DiagnosisService
  ├── TeachBackService
  ├── MasteryService
  └── ReviewService (P2)
       │
       ├── Domain rules + validated JSON content bank
       ├── LLM adapter (optional; constrained tasks only)
       ├── Voice adapters (optional; TTS and STT separate)
       └── Repositories / SQLAlchemy
                 │
                 ▼
          SQLite (local/tests)
          PostgreSQL (deployed environment)
```

### Architecture rules

-   UI code calls service functions; it does not issue SQL or construct
    prompts directly.
-   Services own workflow orchestration and transactions.
-   Domain functions are deterministic and testable without Streamlit,
    network access, or an LLM.
-   Repositories own database reads/writes.
-   Provider adapters wrap external LLM and speech APIs. Do not leak
    provider-specific response types into domain logic.
-   Content JSON is version-controlled and teacher-reviewable.
-   The database stores learner activity and results, not a copy of
    every prompt or secret.
-   Use dependency injection or simple constructors for database
    session, LLM adapter, and voice adapter. Avoid a heavy
    dependency-injection framework.

### Stack decision

  -----------------------------------------------------------------------
  Layer                   Decision                Reason
  ----------------------- ----------------------- -----------------------
  UI                      Streamlit               Fits the existing
                                                  Python-first project
                                                  and beginner team

  Backend/application     Python service layer in No separate API server
                          same app                needed for this scope

  Validation              Pydantic models         Validate structured
                                                  content and model
                                                  outputs

  ORM                     SQLAlchemy 2.x          Consistent database
                                                  access and easier
                                                  SQLite/PostgreSQL
                                                  portability

  Local database          SQLite                  Easy local development
                                                  and tests

  Deployed database       PostgreSQL              Persistent,
                                                  multi-connection
                                                  production database

  Schema migrations       Alembic                 Explicit, repeatable
                                                  schema changes

  Content                 Versioned JSON          Auditable approved
                                                  material and fixed
                                                  question bank

  Testing                 pytest; Streamlit       Domain, integration,
                          AppTest where useful    and UI behavior checks

  Lint/type checks        Ruff; mypy or pyright   Catch common defects
                          if adopted              without excessive
                                                  tooling

  CI                      GitHub Actions          Run checks on every
                                                  push/PR

  Voice                   ElevenLabs TTS if       Optional adapters with
                          configured; separately  fallback
                          verified STT            

  Deployment              Streamlit-compatible    Simple operations;
                          host + managed          confirm host filesystem
                          PostgreSQL              persistence rules
  -----------------------------------------------------------------------

Do not add FastAPI just to call the app "full stack." Add it only if the
product genuinely needs a separate frontend/API or external clients. Do
not use a local SQLite file as the sole production database on an
ephemeral deployment filesystem.

------------------------------------------------------------------------

## 4. Repository structure

Adapt to the existing repository instead of enforcing this layout
blindly. For a new or already modular repository, target:

``` text
learnloop-ai/
├── app.py
├── pages/
│   ├── 1_Learn.py
│   ├── 2_Progress.py
│   └── 3_Settings.py
├── src/
│   └── learnloop/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       │   ├── models.py
│       │   ├── diagnosis_rules.py
│       │   ├── mastery_rules.py
│       │   └── assessment_rules.py
│       ├── services/
│       │   ├── tutor_service.py
│       │   ├── assessment_service.py
│       │   ├── diagnosis_service.py
│       │   ├── teachback_service.py
│       │   ├── mastery_service.py
│       │   └── review_service.py
│       ├── repositories/
│       │   ├── attempts.py
│       │   ├── assessments.py
│       │   ├── learners.py
│       │   ├── mastery.py
│       │   └── review_tasks.py
│       ├── db/
│       │   ├── base.py
│       │   ├── session.py
│       │   ├── models.py
│       │   └── migrations/
│       ├── providers/
│       │   ├── llm.py
│       │   ├── elevenlabs_tts.py
│       │   └── speech_to_text.py
│       ├── ui/
│       │   ├── components.py
│       │   ├── theme.py
│       │   └── state.py
│       └── schemas/
│           ├── diagnosis.py
│           └── teachback.py
├── data/
│   ├── fractions_chapter.json
│   ├── questions.json
│   ├── activities.json
│   └── rubric.json
├── tests/
│   ├── unit/
│   ├── integration/
│   └── ui/
├── scripts/
│   └── seed_demo.py
├── .streamlit/
│   └── config.toml
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── Dockerfile                 # optional, if selected host requires it
├── README.md
├── context.md
└── LICENSE                    # choose an appropriate license before release
```

Avoid empty modules and unnecessary abstractions. If the current app is
small, a smaller equivalent layout is acceptable so long as UI, domain
rules, persistence, and providers remain separate.

------------------------------------------------------------------------

## 5. Data model and database design

Use SQLAlchemy models with explicit foreign keys, constraints, indexes,
timestamps, and migrations. Use UUIDs or stable opaque IDs for
learner/session identifiers; never rely on row order. Store timestamps
in UTC and convert for display.

### Tables

#### `learners`

-   `id` UUID/string primary key.
-   `display_name` nullable.
-   `created_at`, `updated_at`.
-   `is_demo` boolean.
-   A learner is not authenticated merely because an ID exists in the
    browser. If publicly deployed, add authentication or a secure
    single-user gate before exposing learner records.

#### `learning_sessions`

-   `id` primary key.
-   `learner_id` foreign key.
-   `chapter_id`, `content_version`.
-   `current_stage` enum/string.
-   `started_at`, `completed_at`.
-   `status` (`in_progress`, `completed`, `abandoned`).
-   Used to resume or audit a learning loop without relying only on
    Streamlit session state.

#### `attempts`

-   `id` primary key.
-   `learner_id`, `session_id` foreign keys.
-   `question_id`, `concept_id`, `content_version`.
-   `response_text` or normalized `answer_json`.
-   `reasoning_text` nullable.
-   `is_correct` boolean nullable only when not objectively gradable.
-   `reasoning_status` (`valid`, `invalid`, `unclear`, `not_assessed`).
-   `diagnosis_code` enum (`M1`, `M2`, `M3`, `M4`, `S1`, `U1`, `NONE`)
    nullable.
-   `diagnosis_certainty` (`high`, `medium`, `low`, `unknown`).
-   `diagnosis_evidence` text.
-   `clarification_required` boolean.
-   `activity_id` nullable.
-   `source` (`typed`, `speech_transcript`, `choice`).
-   `created_at`.
-   `follow_up_to_attempt_id` nullable self-reference for a retry or
    follow-up.
-   Do not overwrite an earlier attempt when a student retries. Append a
    new record and link it.

#### `assessment_runs`

-   `id` primary key.
-   `learner_id`, `session_id` foreign keys.
-   `phase` (`pre`, `post`).
-   `assessment_version`.
-   `started_at`, `completed_at`.
-   Unique constraint appropriate to product policy: one completed pre
    and one completed post per session, unless retakes are explicitly
    supported.

#### `assessment_responses`

-   `id` primary key.
-   `assessment_run_id` foreign key.
-   `question_id`, `concept_id`.
-   `answer_json` or text.
-   `is_correct` boolean.
-   `answered_at`.
-   Unique `(assessment_run_id, question_id)` to prevent accidental
    duplicate responses in one run.
-   Store actual answers; calculate scores from these rows, never from
    manually typed dashboard values.

#### `teachback_submissions`

-   `id` primary key.
-   `learner_id`, `session_id` foreign keys.
-   `content_version`, `response_text`, `input_source`.
-   `created_at`.
-   Keep only the transcript needed for educational feedback. Do not
    store raw audio unless necessary and explicitly disclosed.

#### `teachback_evaluations`

-   `id` primary key.
-   `submission_id` foreign key.
-   `rubric_version`.
-   `criterion_results_json` validated against the rubric schema.
-   `earned_points`, `possible_points`, `coverage_percent`.
-   `overall_feedback`.
-   `created_at`.
-   Coverage is an explanation rubric score, not an absolute knowledge
    percentage.

#### `concept_mastery`

-   Composite primary key `(learner_id, concept_id)`.
-   `status` (`not_assessed`, `developing`, `practising`, `mastered`).
-   `score` nullable numeric.
-   `evidence_attempt_count`, `distinct_question_count`.
-   `last_evidence_at`, `updated_at`.
-   `policy_version`.
-   This table is a cached summary; it must be reproducible from
    attempts. Provide a service/command to recompute it.

#### `review_tasks` (P2)

-   `id`, `learner_id`, `concept_id`.
-   `reason`, `due_at`, `status` (`due`, `completed`, `dismissed`).
-   `source_attempt_id` nullable.
-   `created_at`, `completed_at`.
-   This is a review queue, not a background notification scheduler.

### Database implementation requirements

-   Use SQLAlchemy sessions and context managers.
-   Commit only after the entire service operation succeeds; rollback on
    exception.
-   Use parameterized ORM queries; never concatenate user input into
    SQL.
-   Add indexes for common lookups: learner + timestamp, session ID,
    concept ID, assessment run + question ID, review due date + status.
-   Use Alembic migrations; do not rely solely on `create_all()` for
    production schema evolution.
-   Include a migration for every schema change.
-   Add a safe seed script that is idempotent and only inserts fixed
    approved content metadata if needed. Do not seed fake student
    progress in normal production mode.
-   In tests, use a temporary SQLite database per test or test session
    and clean it afterward.
-   In production, use PostgreSQL `DATABASE_URL`; local development can
    default to SQLite.
-   Do not put a live database file, learner export, or secret in Git.

### Persistence and privacy

For a public deployment, do not expose a shared anonymous learner
database. Choose one: 1. authenticated users with ownership checks on
every query, or 2. a private single-user deployment behind an access
gate.

Do not introduce a full multi-role school system for the MVP. Still
protect any learner data that is stored. Document retention/deletion
behavior and provide a way to clear demo data.

------------------------------------------------------------------------

## 6. Content bank and mathematical correctness

All scored content is version-controlled JSON and reviewed by a human.
Include `content_version`, `reviewed_by` (or reviewer label),
`reviewed_at`, and source/reference notes. If source notes are internal
teacher material, respect its usage rights.

### Concepts

-   `C1`: Understanding fractions --- numerator, denominator,
    equal-sized parts, fraction as quantity.
-   `C2`: Comparing fractions --- equal numerators, equal denominators,
    common denominator/equivalent fraction methods; denominator does not
    independently determine fraction size.
-   `C3`: Equivalent fractions --- same value; multiply or divide
    numerator and denominator by the same nonzero factor; invalid
    transformations.

### Misconception library

-   `M1` Whole-number bias: compares denominator values as whole numbers
    (e.g. "2/5 is larger than 2/3 because 5 is larger than 3").
    Remediation: same-size fraction strips.
-   `M2` Reversed denominator rule: claims a larger denominator always
    means a larger fraction when numerators are equal. Remediation:
    compare the size of one piece from equal-sized wholes partitioned
    differently.
-   `M3` Numerator-only comparison: compares numerators and ignores
    denominators. Remediation: visual comparison and/or common
    denominators with examples where numerator-only comparison fails.
-   `M4` Invalid equivalent-fraction transformation: assumes adding the
    same number to numerator and denominator preserves value.
    Remediation: compare `1/2` and `2/3`; demonstrate proportional
    scaling.
-   `S1` Likely arithmetic/transcription slip: the method is
    conceptually valid, but a calculation or copying error produces the
    wrong result. Remediation: retry a similar calculation and inspect
    the step.
-   `U1` Insufficient evidence: no reasoning, contradictory reasoning,
    or evidence that does not distinguish categories. Remediation: ask a
    focused clarifying question.
-   `NONE`: no supported misconception; still evaluate reasoning
    separately from answer correctness.

These are hypotheses, not a complete taxonomy. The system must not force
a diagnosis if evidence is insufficient.

### Question record schema

Each question must include: - stable `question_id`, `concept_id`,
`content_version`; - `question_text`, `question_type`, `difficulty`; -
`options` if applicable; - canonical `correct_answer`; - deterministic
`accepted_answers` or grading rule; - `verified_explanation`; -
`learning_objective`; - `is_transfer_question`; -
`misconception_mappings`; - `remediation_activity_ids`; - optional
`source_reference`.

Validate the JSON on startup and fail with a readable error if IDs are
duplicated, required fields are missing, a question refers to an unknown
concept/activity, or an answer key is invalid.

### Six fixed assessment items

Exactly two pre/post items per concept. Keep their IDs and content
stable between phases. Version the assessment bank; if content changes,
start a new assessment version rather than comparing incompatible items.
Do not show the complete answer key before the post-assessment. A
minimal six-item design must include a transfer question or otherwise
clearly disclose that transfer was not assessed.

------------------------------------------------------------------------

## 7. Diagnostic engine

### Input contract

``` json
{
  "question_id": "Q_COMPARE_01",
  "student_answer": "2/5",
  "reasoning_text": "Five is bigger than three.",
  "prior_evidence": [],
  "content_version": "fractions-v1"
}
```

### Output contract

``` json
{
  "question_id": "Q_COMPARE_01",
  "is_correct": false,
  "reasoning_status": "invalid",
  "diagnosis_code": "M1",
  "certainty": "high",
  "evidence": "The learner explicitly compared denominator values as whole numbers.",
  "clarification_required": false,
  "clarifying_question": null,
  "next_activity_id": "A_FRACTION_STRIPS"
}
```

This is an illustrative schema, not a predetermined result. Validate it
with Pydantic and check all IDs against the approved content bank.

### Classification sequence

1.  Grade the answer deterministically using the approved key.
2.  Check if the question's choice/answer has a known deterministic
    misconception mapping.
3.  Inspect the student's reasoning separately from answer correctness.
4.  Use deterministic phrase/rule matching only where it is robust;
    otherwise call the optional LLM adapter.
5.  Give the LLM only the question, canonical answer, approved
    misconception definitions, approved activity IDs, student
    answer/reasoning, and minimal relevant context.
6.  Require a strict JSON/schema response.
7.  Reject unknown codes, unknown activities, invalid fields,
    unsupported claims, or mismatched question IDs.
8.  On uncertain or invalid output, use `U1` and ask a clarification
    rather than guessing.
9.  Store the evidence and selected activity.
10. After remediation, capture a new attempt to determine whether the
    student's reasoning changed.

Do not use the LLM's self-reported confidence as a calibrated
probability. Use coarse certainty categories only as an operational
signal and validate them against evidence. Do not expose `M1` or
internal certainty labels as the primary student-facing copy.

### Example expected distinctions

Student A: "2/5 is larger because five is bigger than three."\
Expected: M1 if evidence supports whole-number comparison;
fraction-strip activity.

Student B: "A fraction with a larger denominator is always larger."\
Expected: M2 only when the reasoning supports a reversed denominator
rule; compare pieces of equal-sized wholes.

Student C: wrong answer, no explanation.\
Expected: U1 and a clarification question, not an invented diagnosis.

Student D: correct option but says "I picked it randomly" or gives
invalid reasoning.\
Expected: answer correctness can be true, reasoning status not
valid/unclear, and mastery must not treat it as demonstrated
understanding.

Student E: uses a valid common-denominator method but makes a single
subtraction/multiplication slip.\
Expected: S1 only when the recorded working supports that
interpretation.

------------------------------------------------------------------------

## 8. Teaching, remediation, and conversation state

### Lesson object

Each concept lesson contains: - plain-language definition; - intuitive
example or analogy; - step-by-step worked example; - optional visual or
accessible text equivalent; - short comprehension question; - common
mistakes; - verified explanation; - content source/reviewer metadata.

The UI displays approved lesson content directly. An LLM may simplify
wording or answer a question using retrieved approved material, but it
must not invent mathematical facts or silently expand the syllabus. When
no provider is configured, use the verified lesson and deterministic
FAQ/feedback.

### Conversation state

Use a small state machine where needed:

`WELCOME → PRE_ASSESSMENT → TEACHING → ASKING_QUESTION → AWAITING_RESPONSE → DIAGNOSING → CLARIFYING or REMEDIATING → TEACH_BACK → EVALUATING → TARGETED_REVISION → POST_ASSESSMENT → COMPLETE`

Persist important workflow state in the database. Streamlit session
state is for transient UI state, not the only source of truth. Validate
transitions and prevent skipping the pre-assessment or submitting the
same answer twice due to reruns.

### Remediation activity object

-   `activity_id`
-   `concept_id`
-   `title`
-   `purpose`
-   `instructions`
-   `question_ids`
-   `target_diagnosis_codes`
-   `expected_learning_evidence`
-   `content_version`

Activity selection must be deterministic from the validated
diagnosis/activity mapping. Store which activity was delivered and the
learner's subsequent result.

------------------------------------------------------------------------

## 9. Teach-back evaluation

Prompt the student:

> Explain what you understood about this topic in your own words. You
> can use an example to help explain your thinking.

### Required rubric criteria

-   `R1`: Explains numerator and denominator correctly.
-   `R2`: Understands that fraction parts must be equal-sized.
-   `R3`: Explains how the number of equal parts affects each part's
    size.
-   `R4`: Compares fractions using a valid method.
-   `R5`: Explains equivalent fractions correctly.

Each criterion status must be exactly one of: - `demonstrated` -
`partial` - `incorrect` - `not_demonstrated`

Every criterion must appear in the result, with evidence grounded in the
actual response. The evaluator must not invent statements or reward
verbosity over correctness.

### Scoring

-   demonstrated = 1
-   partial = 0.5
-   incorrect = 0
-   not_demonstrated = 0

`rubric_coverage = earned_points / possible_points * 100`

Display this as "explanation score" or "rubric coverage", never as a
definitive "knowledge percentage". Explain that not demonstrated means
the student did not show the evidence in this response; it does not
prove they lack the knowledge.

If the response is too short, ambiguous, or affected by a likely
speech-recognition error, ask a targeted follow-up question before
treating the criterion as incorrect. Keep raw AI output separate from
validated results and never persist an invalid evaluation as
authoritative.

### Validated output shape

``` json
{
  "criterion_results": [
    {
      "criterion_id": "R1",
      "status": "demonstrated",
      "evidence": "The learner states what the numerator counts."
    },
    {
      "criterion_id": "R4",
      "status": "not_demonstrated",
      "evidence": "No fraction-comparison method appears in the response."
    }
  ],
  "overall_feedback": "You explained the parts of a fraction clearly. You have not yet shown how to compare fractions with different numerators and denominators.",
  "recommended_concepts": ["C2"],
  "clarification_required": false
}
```

Validate exact criterion IDs and statuses, and ensure the output
contains every required criterion exactly once.

------------------------------------------------------------------------

## 10. Mastery rules

Mastery is a derived summary of actual saved evidence, not lesson
completion or self-report. Keep the policy version in the record.

A transparent prototype policy: - No valid evidence → `not_assessed`. -
Too little evidence → `developing`. - Mixed or inconsistent performance
→ `practising`. - `mastered` only after at least four valid attempts
across at least three distinct questions, at least 80% weighted
performance, and a correct transfer question with valid reasoning.

These are configurable prototype thresholds, not validated educational
standards. Make the policy explicit in code and documentation. A correct
answer with invalid reasoning should not count as a fully demonstrated
attempt. Repeated answers to the same item must not inflate the
distinct-question count.

Recompute mastery from attempts using a pure function. Persist the
summary as a cache for convenient reads, but include a test proving that
a recomputation yields the same result. Display evidence count and last
evidence date alongside mastery status.

------------------------------------------------------------------------

## 11. Assessment and reporting

### Pre/post rules

-   Use the same six question IDs, content version, scoring rules, and
    order policy for pre and post.
-   Persist each answer before moving to the next question.
-   Do not reveal the complete answer key before post-assessment.
-   Prevent duplicate answer rows within one run.
-   A partially completed assessment is not a completed six-item score.
    Show progress, but don't compare incomplete runs as if they were
    complete.
-   Retakes must be explicit and create new assessment runs rather than
    silently overwriting historical evidence.

### Formulas

`score_percent = correct_responses / valid_responses * 100`

`score_change_pp = post_score_percent - pre_score_percent`

Use percentage points, not "percent improvement", for the difference.
Round only for display, not before calculation.

For each learner, report pre and post numerator/denominator,
percentages, score change in percentage points, concept-level results,
and assessment version. For multiple learners, include only learners
with complete paired results in the paired sample count and mean paired
change. Do not present a single learner's n=1 result as population-level
evidence.

### Limitations displayed in the report

-   Reusing identical items can introduce a practice effect.
-   A small uncontrolled pre/post comparison cannot establish that the
    tutor caused the change.
-   Results depend on the quality and coverage of the fixed items.
-   A short assessment may not measure long-term retention or transfer
    comprehensively.

All metrics must be queried or computed from persisted assessment
responses. Never hardcode demo scores into the dashboard. If demo data
is included, label it conspicuously as sample data and keep it isolated
from real learner records.

------------------------------------------------------------------------

## 12. UI and visual design specification

Use the Anthropic frontend-design skill as a design brief, not as a
requirement to add a JavaScript frontend. Read the skill file from the
requested repository before implementation:
`https://github.com/anthropics/skills/tree/main/skills/frontend-design`.
Its key working method is to plan a distinct visual direction, critique
generic defaults, and then implement with intentional typography, color,
spacing, composition, and state design.

### Proposed visual direction: "The learning notebook"

A calm, editorial learning workspace inspired by annotated maths
notebooks, paper, ink, and focused study---not a generic AI dashboard.

Suggested tokens (the designer may refine after reviewing the existing
UI): - Deep ink: `#172A3A` - Paper: `#F7F4EC` - Learning teal:
`#167D78` - Warm correction amber: `#D88A2D` - Muted slate: `#687782` -
Error red: `#B4473D`

Use a characterful display face paired with a highly legible body face;
verify font loading and provide fallbacks. Do not use default "AI purple
gradient on white" styling. Keep contrast accessible and use color plus
text/icon labels for statuses.

### Main navigation

-   **Learn** --- current lesson, quiz, reasoning, remediation,
    teach-back.
-   **Progress** --- mastery evidence, attempts, pre/post report, due
    review tasks if implemented.
-   **Settings** --- optional voice status, data/privacy controls,
    content version, reset demo data.

### Screen requirements

1.  **Welcome / chapter overview**
    -   Product name and plain-language purpose.
    -   Chapter "Comparing fractions".
    -   Three concepts and their objectives.
    -   Visible teacher-support disclaimer.
    -   "Start baseline assessment" action.
2.  **Pre-assessment**
    -   One question at a time, progress indicator, answer controls,
        back/next policy.
    -   Do not display the answer key or explanatory feedback before the
        assessment is submitted.
    -   Save each response and show recoverable errors.
3.  **Lesson**
    -   One concept at a time.
    -   Definition, worked example, optional fraction-strip visual,
        short check.
    -   "Listen" button only when TTS is available; otherwise
        hide/disable with a clear message.
4.  **Reasoning and diagnosis**
    -   Ask "What made you choose that answer?" after a wrong answer or
        when reasoning is required.
    -   Show clarification question if evidence is insufficient.
    -   Explain the likely issue in student-friendly language.
    -   Show the targeted activity and then a follow-up question.
    -   Do not expose internal diagnosis codes as the main UI.
5.  **Teach-back**
    -   Show the exact prompt.
    -   Large labelled text area and submit action.
    -   If voice is available, microphone state, stop control, editable
        transcript, and text fallback.
    -   Warn before leaving with unsaved input.
6.  **Feedback / targeted revision**
    -   List rubric criteria with "shown", "partly shown", "incorrect",
        or "not yet shown".
    -   Give evidence-linked feedback and a next activity.
    -   Explain rubric coverage honestly.
7.  **Progress and report**
    -   Pre/post results, change in percentage points, concept-level
        evidence, attempts, mastery status, evidence count, review
        queue.
    -   Sample size and limitations visible near the result.
    -   Empty state tells the user what to do next rather than
        displaying fake metrics.

### Interaction and accessibility

-   Use consistent labels: "Save answer", "Continue", "Try a similar
    question", "Listen", "Stop recording".
-   Provide clear loading, success, empty, error, unavailable-provider,
    and permission-denied states.
-   Do not depend on hover; support keyboard navigation.
-   Every input has a label; errors are associated with the input.
-   Keep text readable and line length controlled; use semantic headings
    and sensible spacing.
-   Provide text alternatives for fraction-strip visuals and chart
    summaries.
-   Respect reduced-motion preferences for any custom CSS animation.
-   Do not add animations that delay answering or conceal educational
    state.
-   Use Streamlit's multipage navigation API where supported by the
    installed version; otherwise retain the existing working navigation
    approach.
-   Keep styling in a central theme/CSS file, not scattered across page
    scripts. Use only supported Streamlit HTML/CSS techniques and
    sanitize any dynamic content.

------------------------------------------------------------------------

## 13. LLM integration and prompt contracts

LLM calls are optional provider integrations. The app must remain
educationally usable without credentials or network access.

### Provider interface

Create a small interface with methods such as: -
`classify_reasoning(input) -> DiagnosisCandidate` -
`evaluate_teachback(input) -> TeachBackCandidate` - optionally
`rephrase_approved_explanation(input) -> str`

Use Pydantic for request/response schemas. The provider adapter owns
timeouts, retries (bounded), provider-specific SDK details, and error
normalization. Never retry indefinitely. Do not log student response
text by default.

### Diagnosis prompt

Provide only: - approved question and answer; - student answer and
reasoning; - approved misconception definitions; - allowed activity
IDs; - relevant, minimal prior evidence; - strict JSON schema and
uncertainty rules.

Tell the model: - Do not invent a misconception. - If evidence is
insufficient, return `U1` and ask one focused clarification. - Separate
answer correctness from reasoning validity. - Use only approved IDs. -
Evidence must quote or accurately paraphrase the student's actual
reasoning. - Return no extra fields.

### Teach-back prompt

Provide approved lesson material, the full rubric, and the learner
response. Require every rubric criterion exactly once, approved status
enums only, and evidence grounded in the response. "Not demonstrated"
must not be turned into "incorrect" without explicit contrary evidence.

### Output validation

1.  Parse response.
2.  Validate schema and enum values.
3.  Check question, concept, rubric, and activity IDs against the
    approved content.
4.  Check all required rubric criteria appear exactly once.
5.  Reject malformed or inconsistent results.
6.  On failure, use a deterministic fallback or ask a clarification.
7.  Record provider error category without storing secrets or
    unnecessarily storing raw provider responses.

Do not build a generic agent that controls all application actions. The
application service, not the LLM, controls state transitions and
database writes.

------------------------------------------------------------------------

## 14. Voice design

### Text-to-speech

-   Use ElevenLabs only when the API, model/voice, account limits, and
    credentials have been verified.
-   Send only the approved visible explanation/feedback text.
-   Keep text visible; audio is supplementary.
-   Provide play/replay and a useful failure state.
-   Cache audio only if safe, useful, and within provider terms; avoid
    caching learner-sensitive text unnecessarily.
-   Keep the API key server-side in environment configuration.

### Speech-to-text

TTS and STT are separate capabilities. Select and verify one
transcription route before implementation: - a supported browser
speech-recognition API, with explicit browser compatibility checks; or -
a server-side STT provider.

When entering teach-back, request permission and attempt auto-start only
when the browser/provider supports it and the user has clearly initiated
the interaction. Display a visible recording indicator and stop button.
Let the learner edit the transcript before submitting it. Never treat
transcription errors as evidence of a misconception.

If voice fails, text input must remain fully functional. Do not claim
voice is implemented merely because a button exists.

------------------------------------------------------------------------

## 15. Security, privacy, and reliability

### Secrets and configuration

-   Use environment variables or the host's secret manager; `.env` is
    local-only and ignored by Git.
-   Commit `.env.example` containing variable names and safe
    placeholders only.
-   Never expose provider keys in Streamlit-rendered HTML, JavaScript,
    logs, or client-visible state.
-   Rotate any credential that has ever been committed or shared.
-   Validate configuration at startup, but missing optional LLM/voice
    keys should disable those features---not crash the core app.

Suggested settings: - `APP_ENV=development|test|production` -
`DATABASE_URL=sqlite:///./learnloop.db` locally; PostgreSQL URL in
deployment - `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL` -
`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` - STT provider configuration
if selected - `LOG_LEVEL` - `DEMO_MODE=false` by default in production

Use a typed settings object and validate required production
configuration. Avoid scattering `os.getenv()` calls across modules.

### Input and database safety

-   Enforce reasonable maximum lengths for text answers and teach-back.
-   Validate IDs, enum values, and payload sizes.
-   Escape/sanitize any user content displayed as HTML.
-   Use ORM/parameterized queries.
-   Apply database constraints and ownership checks.
-   Do not store raw audio unless explicitly necessary.
-   Do not include personal data in logs or analytics by default.
-   Avoid sending unnecessary learner history to the LLM; send only
    relevant context.
-   Provide clear data deletion/reset behavior and explain what is
    retained.

### Error handling

-   Catch provider timeouts, rate limits, invalid output, and network
    failures at the adapter/service boundary.
-   Return useful user-facing messages without stack traces or secrets.
-   Log diagnostic context with request/session IDs and error category,
    not raw tokens or full private content.
-   Never silently convert an LLM failure into a fabricated diagnosis.
-   Use bounded timeouts and retries; make retries idempotent where
    appropriate.
-   Ensure duplicate button clicks/reruns cannot create duplicate
    assessment answers.
-   A health check or app startup check should validate content files
    and database connectivity without calling paid APIs.

### Real-world deployment boundary

This specification makes the code deployable, but it does not by itself
make the service production-certified. Before public use with real
minors or student records, perform a privacy/security review, confirm
applicable legal requirements, and establish a support/retention
process. For hackathon demos, use fictional learner data.

------------------------------------------------------------------------

## 16. Configuration and local development

Provide: - `pyproject.toml` with project metadata and Ruff
configuration. - Locked or pinned dependencies using the team's chosen
dependency workflow. - `requirements.txt` for the deployment platform if
required. - `requirements-dev.txt` for pytest/lint tooling. -
`.env.example`, `.gitignore`, and a complete README. - `alembic.ini` and
migration files if SQLAlchemy/Alembic are used.

The README must cover: 1. Python version supported by the dependencies.
2. Create and activate virtual environment. 3. Install dependencies. 4.
Configure `.env` / secrets. 5. Initialize/migrate database. 6. Start
app. 7. Run unit/integration/UI tests. 8. Run lint/type checks. 9. Seed
or reset demo data. 10. Deploy and configure hosted database/secrets.
11. Troubleshoot missing provider credentials and database connection
failures. 12. State current limitations and which features are optional.

Example commands (adjust to the actual repo):

``` bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
alembic upgrade head
streamlit run app.py
pytest
ruff check .
ruff format --check .
```

Do not publish these as guaranteed commands until the files and entry
point exist.

------------------------------------------------------------------------

## 17. Testing strategy

### Unit tests

-   Correct fraction comparisons and equivalent fraction rules.
-   All supported misconception mappings.
-   `U1` fallback when evidence is missing or contradictory.
-   Correct answer with invalid reasoning.
-   Distinction between S1 and conceptual misconception.
-   Teach-back scoring and every rubric status.
-   Missing criterion / duplicate criterion / unknown activity
    validation.
-   Mastery thresholds, distinct-question count, and transfer-question
    requirement.
-   Pre/post calculations, rounding, and percentage-point change.
-   Content-bank schema, duplicate IDs, missing references, and invalid
    answer keys.

### Integration tests

-   Database write/read for a learning attempt.
-   A diagnosis produces the expected approved remediation activity.
-   Remediation result links to the originating attempt.
-   Teach-back submission and evaluation persist.
-   Assessment answers survive a new database session.
-   Post-assessment uses the same six question IDs as pre-assessment.
-   Mastery recomputation matches stored summary.
-   Provider timeout/invalid JSON leaves deterministic flow usable.
-   Database transaction rollback prevents partial writes.

### UI tests

Use Streamlit AppTest where practical, supplemented with manual browser
checks: - Welcome → pre-assessment → lesson → diagnostic → teach-back →
revision → post-assessment → report. - Refresh/reopen preserves saved
records. - Empty-state and error-state rendering. - Voice
disabled/permission denied still supports text. - Responsive layout and
keyboard navigation.

### Acceptance cases

A. Correct answer + sound reasoning: correctness and reasoning saved;
mastery changes only if policy threshold is met.\
B. M1 wording: diagnoses M1 when evidence supports it; selects fraction
strips.\
C. M2 wording: distinct M2 activity when evidence supports it; not
automatically M1.\
D. Wrong answer without reasoning: U1/clarification; no invented
diagnosis.\
E. Correct option with invalid reasoning: correct answer saved but
understanding not marked demonstrated.\
F. Partial teach-back: all criteria evaluated; missing and incorrect
separated; targeted revision selected.\
G. Persistence: records survive app rerun and database session change.\
H. Pre/post: same six IDs, scores calculated from rows, correct
percentage-point change and paired n.\
I. Voice failure: visible message and working text fallback.\
J. LLM failure: app continues with approved content and deterministic
grading.\
K. Security: no secrets in Git; public access cannot read another
learner's records.\
L. Deployment: clean environment can install, migrate, start, and load
the chapter.

Never describe a test as passed unless it was actually executed and its
result checked.

------------------------------------------------------------------------

## 18. CI and deployment

### GitHub Actions

On every push and pull request: 1. Set up the supported Python version.
2. Install dependencies. 3. Run Ruff lint and format check. 4. Run
pytest. 5. Optionally run type checks. 6. Do not require real provider
credentials in CI; use mocked adapters. 7. Never print secrets in CI
logs.

Use a small workflow. Avoid deploying automatically from unreviewed
branches.

### Deployment steps

1.  Choose a host compatible with Streamlit or container deployment.
2.  Provision persistent PostgreSQL for production.
3.  Configure environment variables through the host secret manager.
4.  Run Alembic migrations as a controlled release step.
5.  Deploy the app from a known Git commit.
6.  Confirm app startup and database connection.
7.  Run a smoke test with a fictional learner.
8.  Verify records persist across application restart/redeploy.
9.  Verify LLM/voice can be disabled without breaking the learning flow.
10. Confirm no test credentials or seeded fake progress appear in
    production.
11. Document rollback to the previous app version and database
    backup/restore procedure.

If using Streamlit Community Cloud or another host, verify its current
filesystem and database persistence rules rather than assuming a local
SQLite file survives restarts. Use the provider's supported secrets
mechanism.

### Deployment definition of done

-   A fresh environment can install and start the app.
-   Database migrations apply cleanly.
-   Health/startup checks validate the content bank.
-   The six-question flow completes.
-   Results persist in the hosted database.
-   Provider outages do not break core learning.
-   Logs do not contain secrets or unnecessary student content.
-   A previous release can be restored using documented steps.

------------------------------------------------------------------------

## 19. Git workflow and mandatory GitHub push

The coding agent must commit at appropriate checkpoints and push the
completed work when permitted. Do not make one giant end-of-task commit.

### Initial checks

``` bash
git status --short --branch
git remote -v
git branch --show-current
```

If the working tree contains user changes, preserve them. Do not
discard, reset, or overwrite them. If there is no remote, do not invent
a GitHub repository URL; ask the user to configure one or clearly report
that pushing is blocked.

### Suggested commit sequence

Commit names should reflect actual changes, for example:

1.  `docs: record implementation plan and architecture`
2.  `feat: validate approved fractions content bank`
3.  `feat: add deterministic diagnosis and remediation rules`
4.  `feat: implement learning and teach-back workflow`
5.  `feat: persist attempts and assessment runs`
6.  `feat: calculate mastery and pre-post report`
7.  `feat: add optional voice adapters`
8.  `test: cover end-to-end learning loop`
9.  `chore: add deployment and CI configuration`

Do not create empty commits or claim features in commit messages before
they work. It is acceptable to combine small related changes if the
repository is tiny, but preserve reviewable history.

### Before each commit

``` bash
git diff --check
git status --short
git diff --stat
```

Review the actual diff. Run relevant tests and lint. Confirm `.env`,
`.streamlit/secrets.toml`, database files, logs, audio files, and
private data are ignored. Never stage everything blindly if untracked
user files exist; inspect `git status` and stage explicit paths.

### Before push

``` bash
pytest
ruff check .
ruff format --check .
git status --short
git log -5 --oneline
```

Then push the current branch to its configured remote:

``` bash
git push -u origin "$(git branch --show-current)"
```

Use the actual configured remote name if it is not `origin`. Never use
`--force` as a workaround. If authentication, network, permissions, or
remote configuration prevents pushing: - do not claim that the push
succeeded; - preserve local commits; - show the exact safe command or
missing setup needed; - report the remote and branch without exposing
credentials.

After pushing, verify the push command succeeded and the local branch is
no longer ahead of its remote tracking branch, where available. Report
the commit hashes and branch.

------------------------------------------------------------------------

## 20. Team implementation and integration

For a four-person team: - **Content owner:** lessons, six assessment
items, answer keys, rubric, misconception/activity mappings. -
**Learning-engine owner:** deterministic grading, diagnosis,
clarification, remediation selection, LLM schema validation. -
**UI/voice owner:** Streamlit screens, state transitions, accessibility,
optional TTS/STT. - **Data/testing owner:** SQLAlchemy models,
migrations, repositories, mastery, assessment report, tests, deployment
checks.

Agree on shared Pydantic contracts before parallel work. Merge
continuously. Each contributor should work on a branch or clearly
assigned files; do not wait until the last hour to integrate. The
integration owner is responsible for a working end-to-end path, not just
separate modules.

------------------------------------------------------------------------

## 21. Recommended implementation sequence

1.  **Audit** current repository and `context.md`; preserve existing
    work.
2.  **Stabilize contracts** for content JSON, diagnosis output,
    teach-back output, database records, and service functions.
3.  **Validate content** and add deterministic grading.
4.  **Implement diagnosis** with M1--M4, S1, U1, NONE and distinct
    remediation mapping.
5.  **Complete the text learning loop** in the UI, including
    clarification and follow-up.
6.  **Implement teach-back** and rubric evaluation with strict
    validation.
7.  **Add persistence** and migrations; prove attempts survive reruns.
8.  **Implement mastery** as a reproducible pure calculation.
9.  **Implement fixed pre/post assessment** and honest report.
10. **Run all P0 acceptance tests** and fix blockers.
11. **Polish UI** using the frontend design skill; check
    empty/error/loading states and accessibility.
12. **Add P1 voice** only after P0 passes.
13. **Add P2 review queue** only if time remains.
14. **Add CI and deployment configuration**.
15. **Commit and push** in small verified checkpoints.
16. **Final smoke test** from a clean environment and report exactly
    what is verified.

For a short hackathon, simplify scope, not verification. Do not
sacrifice the complete text-based learning loop to chase voice or visual
polish.

------------------------------------------------------------------------

## 22. Demonstration script

Use fictional demo data and show one coherent journey:

1.  Show the teacher-reviewable fractions chapter and three concepts.
2.  Complete the six-item baseline assessment.
3.  Teach comparing fractions.
4.  Submit an incorrect answer with explicit whole-number-bias
    reasoning.
5.  Show that the tutor uses evidence and selects fraction strips.
6.  Run a second case with a reversed denominator rule and show the
    different response.
7.  Submit an ambiguous answer and show a clarifying question.
8.  Complete teach-back and show evidence per rubric criterion.
9.  Open targeted revision for the missing concept.
10. Complete the same six post-assessment items.
11. Show score change, concept evidence, paired sample size, and
    limitations.
12. Refresh/reopen the app to prove persistence.
13. If voice is implemented, play one approved explanation and
    demonstrate transcript editing; otherwise explain that text remains
    the supported fallback.

All results must be generated by the actual workflow or explicitly
marked as sample data.

------------------------------------------------------------------------

## 23. Final response required from the coding agent

At the end of implementation, provide:

1.  **Repository audit:** what existed before and what was preserved.
2.  **Implemented:** features actually completed.
3.  **Tested:** exact commands run and pass/fail results.
4.  **Not implemented / not verified:** honest list of gaps.
5.  **Architecture changes:** files added/changed and why.
6.  **Database:** migration state, local vs deployed database
    configuration.
7.  **Run instructions:** exact commands verified in this repository.
8.  **Environment variables:** names only, never values.
9.  **Deployment:** chosen host, required secrets/configuration,
    smoke-test status.
10. **Git:** commit hashes, branch, remote push result, and any blocker.
11. **Known limitations:** especially assessment validity, diagnosis
    uncertainty, voice support, and privacy.
12. **Next actions:** only the highest-priority remaining items.

------------------------------------------------------------------------

## 24. Definition of done

The project is ready for its intended deployment/demo only when:

-   The current repository has been inspected and existing work
    preserved.
-   Approved fractions content loads and validates.
-   Pre-assessment records six actual answers.
-   Teaching uses approved content.
-   Incorrect answers trigger reasoning analysis.
-   Ambiguous reasoning triggers clarification.
-   Supported misconceptions lead to different targeted activities.
-   Correctness and reasoning are stored separately.
-   Teach-back evaluates all rubric criteria with grounded evidence.
-   Missing concepts trigger targeted revision.
-   Attempts and assessments persist.
-   Mastery can be recomputed from actual evidence.
-   Pre/post uses the same six question IDs and reports actual
    percentage-point change, paired sample size, and limitations.
-   LLM failure does not break core functionality.
-   Voice, if enabled, has visible controls and text fallback.
-   Unit, integration, and end-to-end tests pass.
-   Security checks find no committed secrets or exposed learner
    records.
-   The deployment environment uses persistent storage and a verified
    migration process.
-   README/setup instructions are accurate.
-   The changes are committed and pushed to the configured GitHub
    remote, or the exact blocker is reported honestly.

------------------------------------------------------------------------

## 25. Development references

Use the current official documentation and verify version-specific
behavior before implementation:

-   Anthropic frontend-design skill:
    https://github.com/anthropics/skills/tree/main/skills/frontend-design
-   Streamlit multipage navigation:
    https://docs.streamlit.io/develop/concepts/multipage-apps
-   Streamlit deployment concepts:
    https://docs.streamlit.io/deploy/concepts
-   Streamlit secrets:
    https://docs.streamlit.io/develop/concepts/connections/secrets-management
-   Streamlit testing:
    https://docs.streamlit.io/develop/concepts/app-testing
-   SQLAlchemy 2.x documentation: https://docs.sqlalchemy.org/en/20/
-   Alembic migrations: https://alembic.sqlalchemy.org/en/latest/
-   Pydantic validation: https://docs.pydantic.dev/latest/
-   pytest: https://docs.pytest.org/en/stable/
-   Ruff: https://docs.astral.sh/ruff/
-   GitHub Actions: https://docs.github.com/actions
-   ElevenLabs API documentation: https://elevenlabs.io/docs

Do not install a dependency or execute a skill's shell commands merely
because a guide recommends them. Check compatibility, maintenance,
license, security implications, and whether the current codebase
actually needs them.

------------------------------------------------------------------------

## 26. Immediate instruction to the coding agent

**Read `context.md` and inspect the current repository before coding.**
Compare the existing implementation against this specification, create a
prioritized checklist of missing P0 requirements, then implement the
highest-priority missing piece without rewriting working code. Complete
and test the text-based learning loop first. Add voice and the review
queue only after the P0 acceptance tests pass. Commit in small verified
increments and push to the configured GitHub remote when authorized and
available.
