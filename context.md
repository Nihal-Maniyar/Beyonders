# LearnLoop AI --- Master Context for AI Coding Agents

**File:** `context.md`\
**Purpose:** Self-contained product, architecture, implementation, and
quality reference for Google Antigravity and future AI coding agents.\
**Document version:** 1.0\
**Product status:** Approved product direction and architecture
baseline; implementation has not been authorized by this document
alone.\
**Last updated:** 2026-10-11

> **Agent instruction:** Read this file before changing code. Treat the
> requirements and constraints here as the project contract. Inspect the
> real repository before assuming that any described component,
> assessment, database, dependency, or integration already exists. Do
> not claim that a feature is implemented unless you have verified it in
> the repository and tests.

------------------------------------------------------------------------

## 1. Project overview

**LearnLoop AI** is an adaptive, interactive learning assistant. The
initial hackathon MVP focuses exclusively on **fractions** and
demonstrates a complete learning loop: assess the student, ask why they
answered as they did, infer a possible misconception, teach the relevant
concept, provide targeted practice, reassess, and report progress.

The project is being prepared for implementation using **Google
Antigravity**. It is optimized for a short live hackathon demonstration,
not for production-scale school deployment.

### Source-of-truth order

When sources conflict, use this order and report the conflict rather
than silently guessing:

1.  Explicit, most-recent decisions from the project owner.
2.  This `context.md` after it has been reviewed and committed as the
    current master specification.
3.  The approved PRD and architecture/ERD artifacts stored in the
    repository, if present.
4.  Existing code and tests, which are evidence of current behavior but
    do not automatically override approved product requirements.
5.  Assumptions documented in this file.
6.  General conventions.

The repository audit may reveal that a proposed component already exists
or that a planned design is incompatible with the current
implementation. Record findings and propose the smallest safe
reconciliation; do not rewrite working code blindly.

### Status terminology

-   **Required:** Must be implemented for the MVP or live demo.
-   **Conditional:** Implement only if the repository audit confirms the
    need or the owner approves it.
-   **Deferred:** Out of initial scope.
-   **Unresolved:** A decision still needs confirmation. Do not invent
    an answer.

------------------------------------------------------------------------

## 2. Problem statement

Digital learning tools often report whether an answer is right or wrong
without identifying why a student made a mistake. Generic explanations
may not address the student's actual misunderstanding, allowing the same
conceptual error to recur.

LearnLoop AI should use a student's answer and explanation as evidence
to adapt the next teaching step. It should make the reasoning process
visible, offer targeted help, and check whether the student can apply
the concept afterward.

------------------------------------------------------------------------

## 3. Objectives

### Product objectives

1.  Demonstrate one complete, coherent learning loop for fractions.
2.  Capture student reasoning after a relevant answer, especially an
    incorrect one.
3.  Use reasoning and answer evidence to form a **possible**
    misconception hypothesis.
4.  Deliver targeted explanations and follow-up practice.
5.  Compare pre-assessment and post-assessment results when the approved
    assessment policy supports a valid comparison.
6.  Include a meaningful **ElevenLabs-powered voice interaction in the
    live demonstration**.
7.  Keep the learning workflow usable in text if voice services fail.
8.  Preserve the existing Streamlit application as a runnable backup if
    it exists in the repository.

### Engineering objectives

-   Reuse verified educational logic rather than duplicating it in
    JavaScript.
-   Keep frontend, learning logic, persistence, and external-provider
    integration boundaries understandable.
-   Validate all important rules on the backend.
-   Protect anonymous-session data from cross-session access.
-   Build in small, tested increments after implementation approval.
-   Avoid unnecessary infrastructure and dependencies during the
    hackathon.

### Success evidence

The project is successful for the MVP when a rehearsed user journey can
be completed reliably from anonymous session creation through progress
report, including a real ElevenLabs interaction. The demo must not rely
on fabricated API results or a disconnected audio showcase.

------------------------------------------------------------------------

## 4. Target users

### Primary user: student

A learner studying basic fractions. The interface must use plain
language, clear feedback, readable fraction notation, and a low-friction
session start.

### Secondary stakeholder: teacher

A teacher may eventually use the product to define curricula or review
learning progress. Teacher accounts, dashboards, class management, and
syllabus authoring are **not** part of the initial MVP.

### Demo operator

A team member may prepare the demo, configure environment variables, and
run the application. Demo setup must not require the student to create
an account.

------------------------------------------------------------------------

## 5. User roles and permissions

### Anonymous student session

-   No registration, password, or permanent student account.
-   Each learning session has a unique identifier and a high-entropy
    secret/token or equivalent secure session mechanism.
-   The secret authorizes access only to data belonging to that session.
-   The public session ID is not an authorization credential.
-   A session may be active, completed, or expired.
-   A session must not access another session's attempts, answers,
    reasoning, interactions, or report.

### Application/backend

-   Owns scoring, state transitions, session validation, content
    publication checks, and AI/voice integration.
-   Does not trust scores, correctness flags, mastery claims, or
    misconception labels supplied by the browser.
-   Keeps provider credentials server-side.

### Teacher/admin

No teacher/admin role or administrative API is required for the MVP. Do
not add login or role-based access control for hypothetical users
without approval.

------------------------------------------------------------------------

## 6. Functional requirements

### FR-01 --- Anonymous session initialization (Required)

-   Create a new anonymous learning session.
-   Provide a unique session identity.
-   Initialize the learning workflow.
-   Associate all learning events with the session.
-   Validate the session and expiry on every private endpoint.
-   Use a secure browser-session mechanism; prefer an HttpOnly, Secure
    cookie in HTTPS deployments where the deployment topology supports
    it.
-   Define refresh/recovery and retention behavior before
    implementation.

### FR-02 --- Fraction pre-assessment (Required; policy subject to audit)

-   Present the approved set of fraction questions.
-   Record each answer and the relevant attempt.
-   Calculate scores on the server.
-   Preserve the existing assessment implementation until it has been
    inspected.
-   **Do not preserve, alter, or replace existing questions/scoring by
    assumption.** First inspect the repository's questions, answer keys,
    scoring rules, concept tags, state handling, and tests. Record
    findings and obtain/confirm the assessment-policy decision before
    changing behavior.
-   Never send correct-answer flags or scoring internals to the browser
    when they should remain hidden.

### FR-03 --- Fraction lessons (Required)

-   Teach fractions through short learning units and worked examples.
-   Keep content aligned with questions and targeted feedback.
-   Use simple, age-appropriate wording.
-   Reuse existing lesson content where verified and suitable.
-   Do not add unrelated subjects to the MVP.

### FR-04 --- AI tutor (Required)

-   Respond to student questions within the fractions scope.
-   Explain concepts rather than merely disclose answers.
-   Ask the student to explain their reasoning when useful.
-   Use session context and evidence from the learning workflow.
-   Handle uncertain or ambiguous reasoning honestly.
-   Keep the core learning logic on the backend or in the existing
    Python educational engine.

### FR-05 --- Reasoning capture and misconception hypotheses (Required)

-   After a relevant answer, ask a question such as: "Why did you choose
    this answer?"
-   Capture the student's text response; speech transcription may be
    used only if the chosen, verified voice integration supports it and
    it is needed for the approved demo.
-   Associate reasoning with the answer it explains.
-   Treat a misconception as a hypothesis, not a diagnosis.
-   Ask a clarifying question if the evidence is ambiguous.
-   Record enough evidence to explain why a feedback step was selected.

### FR-06 --- Targeted feedback and practice (Required)

-   Explain the relevant concept or error.
-   Provide a worked example, visual explanation, or simpler teaching
    step.
-   Offer a related follow-up question.
-   Use the response to decide whether more teaching or another practice
    item is needed.
-   Do not reveal answers prematurely if the approved assessment policy
    requires delayed feedback.

### FR-07 --- Teach-back and adaptive loop (Required)

-   Complete at least one end-to-end loop: initial answer/mistake →
    reasoning → targeted explanation → follow-up question.
-   Check whether the student can apply the concept after teaching.
-   Continue or advance using documented rules and evidence.
-   Do not claim mastery unless a defined, approved criterion supports
    it.

### FR-08 --- Post-assessment (Required)

-   Record a separate post-assessment attempt.
-   Keep pre-assessment, practice, and post-assessment results
    distinguishable.
-   Compare results only when the approved question set/scoring makes
    the comparison meaningful.
-   Do not silently change assessment policy during implementation.

### FR-09 --- Progress report (Required)

Where supported by recorded data, show: - Pre-assessment score and
maximum. - Post-assessment score and maximum. - Percentage-point change,
when both scores are comparable. - Concepts or skills demonstrated. -
Difficulties or tentative misconceptions. - Practice completed. -
Suggested next learning step.

Clearly distinguish measured assessment results from AI-generated
interpretations. Never fabricate results or claim improvement without
evidence.

### FR-10 --- ElevenLabs voice (Required for live demonstration)

-   The live demo must include at least one meaningful
    ElevenLabs-powered spoken tutor interaction.
-   Prefer a voice moment connected to the learning loop, such as the
    tutor asking why an answer was chosen and responding to the
    student's reasoning.
-   Use a verified ElevenLabs API capability and a valid, owner-provided
    credential. Never invent credentials, endpoints, models, or provider
    capabilities.
-   Keep calls server-side so provider secrets never reach frontend
    bundles or browser-visible responses.
-   Add bounded timeouts and clear failure handling.
-   Keep text tutoring usable when voice fails.
-   Speech-to-text/student speech input is **not automatically
    required**; confirm its need and verify the provider path before
    implementing it. Spoken tutor output is the minimum demo requirement
    unless the owner approves a broader voice interaction.
-   Do not store raw audio by default.

### FR-11 --- Streamlit backup preservation (Required if present)

-   Inspect and identify the current Streamlit entry point and how it is
    run.
-   Preserve a working backup and its required
    dependencies/configuration.
-   Do not delete or overwrite it as part of a React migration.
-   If sharing Python modules or a database, verify compatibility and
    test both paths before relying on shared state.

------------------------------------------------------------------------

## 7. Non-functional requirements

-   **Usability:** A learner can understand what to do next without
    technical instructions.
-   **Responsiveness:** The core journey is fast enough for a live
    demonstration.
-   **Reliability:** Voice or AI-provider failure must not corrupt
    session or assessment state.
-   **Integrity:** Answers, attempts, and scores must be internally
    consistent.
-   **Privacy:** Collect only the data required for the anonymous
    session.
-   **Security:** Enforce session ownership server-side and protect
    provider credentials.
-   **Accessibility:** Keyboard navigation, visible focus, meaningful
    labels, readable contrast, and non-audio alternatives.
-   **Maintainability:** Reuse existing logic and keep module
    responsibilities clear.
-   **Demonstrability:** The live demo can be rehearsed and repeated.
-   **Portability:** Setup instructions must explain the supported local
    and deployed configurations.
-   **Honesty:** Do not claim unimplemented features, verified results,
    mastery, or successful deployment without evidence.

Quantitative latency, uptime, retention, and load targets are not yet
specified. Do not invent service-level objectives.

------------------------------------------------------------------------

## 8. MVP scope

### P0 --- Must work

1.  Anonymous session start.
2.  Fraction pre-assessment.
3.  Fraction lesson content.
4.  Tutor interaction.
5.  Reasoning capture.
6.  Evidence-based misconception hypothesis.
7.  Targeted feedback.
8.  Follow-up practice/teach-back.
9.  Post-assessment.
10. Progress report.
11. ElevenLabs-powered spoken tutor output in the live demo.
12. Text fallback for voice failure.
13. Correct session isolation and data integrity.
14. Preservation of the existing Streamlit backup if present.

### Conditional enhancements

-   Speech-to-text for student answers, only if the verified provider
    capability and demo requirements justify it.
-   Extra fraction difficulty levels.
-   Improved progress visualizations.
-   More detailed misconception summaries.
-   Teacher-facing session review, only with explicit approval.

------------------------------------------------------------------------

## 9. Excluded features

Do not build these as part of the initial MVP unless the project owner
explicitly changes scope:

-   Multiple school subjects.
-   Student registration and login.
-   Teacher/admin accounts.
-   Class enrollment or management.
-   Full teacher dashboard.
-   Automated long-term scheduling of quizzes.
-   Multi-student analytics.
-   Permanent student profiles.
-   Raw audio recording storage.
-   Production-scale microservices or orchestration.
-   Redis, message queues, or background workers without a verified
    requirement.
-   File upload/storage features without a real product need.
-   New curriculum-generation features that are not necessary for the
    fractions learning loop.

------------------------------------------------------------------------

## 10. Complete user workflows

### Workflow A --- Start session

1.  Student opens the app.
2.  Frontend requests an anonymous session.
3.  Backend generates a cryptographically secure secret and session ID.
4.  Backend stores a hash of the secret and session metadata.
5.  Backend sends the secret using the approved secure session
    mechanism.
6.  Frontend transitions to the pre-assessment.
7.  If session creation fails, show a retryable error; do not fabricate
    a session.

### Workflow B --- Pre-assessment

1.  Frontend requests the approved assessment definition.
2.  Backend returns safe question content and options, excluding hidden
    answer keys.
3.  Student submits an answer.
4.  Backend validates session ownership, attempt status, question
    membership, and option membership.
5.  Backend records the answer idempotently and applies the approved
    feedback/scoring policy.
6.  On completion, backend calculates and stores the result
    transactionally.
7.  Frontend shows the next learning step.

### Workflow C --- Reasoning and adaptive tutoring

1.  Student answers a relevant question.
2.  Tutor asks why the student selected that answer.
3.  Student submits text reasoning (or an approved transcript from
    speech input).
4.  Backend stores the reasoning linked to the answer.
5.  Tutoring service uses the question, answer, and reasoning as
    evidence.
6.  It forms a tentative misconception hypothesis or asks for
    clarification.
7.  Tutor explains the concept with a worked example or visual.
8.  Student answers a follow-up question.
9.  The service records the response and chooses the next
    teaching/practice step using approved rules.

### Workflow D --- ElevenLabs voice interaction

1.  Frontend requests spoken output for tutor text through the backend.
2.  Backend validates the session and request size.
3.  Backend calls the verified ElevenLabs integration using a
    server-side credential.
4.  Backend returns audio or a safe playback reference according to the
    verified API flow.
5.  Frontend plays the response and provides accessible text.
6.  On timeout, provider failure, or unsupported audio, show a
    non-blocking notice and retain the text tutor response.
7.  Do not claim voice succeeded until a successful response is
    received.

### Workflow E --- Post-assessment and report

1.  Student completes the learning/practice steps.
2.  Frontend starts the approved post-assessment.
3.  Backend records answers and finalizes the attempt transactionally.
4.  Progress service retrieves valid completed pre/post attempts.
5.  It calculates score comparison only if comparable.
6.  It summarizes evidence-backed concept outcomes and review tasks.
7.  Frontend displays the report.
8.  If either assessment is incomplete or incomparable, display the
    available results and explain that a comparison is unavailable.

### Workflow F --- Retry, interruption, or expiry

-   A retry should create a new attempt number when the product policy
    allows another attempt; it must not overwrite completed historical
    results.
-   Duplicate answer submission must not create duplicate rows or score
    twice.
-   Completing an already completed attempt should be idempotent or
    return a documented conflict without altering the score.
-   Expired sessions must not access protected resources.
-   If recovery after refresh is supported, use the approved
    cookie/session mechanism; do not put secrets in URLs.
-   AI/voice failure must not invalidate already stored answers or
    reasoning.

------------------------------------------------------------------------

## 11. Business rules

1.  The MVP covers fractions only.
2.  No account is required; all activity belongs to an anonymous
    session.
3.  Session secrets are distinct from public session IDs.
4.  Backend validation is authoritative.
5.  Scores are calculated server-side.
6.  A question option must belong to the question being answered.
7.  An assessment attempt can only accept questions assigned to that
    assessment version.
8.  Pre-assessment, practice, and post-assessment results remain
    distinguishable.
9.  Completed assessment versions should be immutable; create a new
    version for material question/scoring changes.
10. Duplicate answer submissions must not change the score twice.
11. Completed attempts cannot accept new answers.
12. An answer may have multiple reasoning responses if clarification is
    needed.
13. A misconception is tentative unless supported by the approved
    confirmation rule.
14. AI inference must not directly modify assessment correctness or
    scores.
15. A progress report is derived from recorded data; do not invent
    missing results.
16. Compare pre/post results only when the assessment policy makes them
    comparable.
17. Voice is required for the live demonstration, but not a prerequisite
    for text-based learning.
18. Provider credentials remain server-side.
19. Raw audio is not stored by default.
20. Preserve the Streamlit backup and avoid destructive repository
    changes.
21. Never replace existing assessment behavior before auditing the
    current implementation and resolving the assessment policy.
22. Keep the architecture lightweight; add dependencies only when they
    solve a verified requirement.

------------------------------------------------------------------------

## 12. Edge cases

Handle and test at least the following:

-   Session creation fails or returns an invalid response.
-   Session token is missing, invalid, revoked, or expired.
-   Student attempts to access another session's attempt or answer.
-   Assessment code is unknown, inactive, or has no questions.
-   Question is archived or not assigned to the selected assessment
    version.
-   Selected option belongs to a different question.
-   Answer is empty, malformed, or outside allowed size.
-   Student submits the same answer twice rapidly.
-   Student navigates away while an attempt is in progress.
-   Attempt completion is requested twice.
-   Attempt has unanswered required questions.
-   AI response is empty, malformed, delayed, or unavailable.
-   Reasoning is ambiguous or does not explain the answer.
-   Misconception confidence is absent or outside the valid range.
-   ElevenLabs credential is missing or invalid.
-   ElevenLabs returns an error, times out, or returns unsupported
    audio.
-   Browser cannot play returned audio.
-   Speech transcript is empty or inaccurate.
-   Post-assessment cannot be compared with pre-assessment.
-   Report has insufficient evidence to claim mastery.
-   Database transaction fails partway through completion.
-   Concurrent requests target the same attempt.
-   Streamlit and the new app would update shared records concurrently.
-   A published question or assessment is modified after attempts have
    used it.

Show actionable user-facing errors, log sanitized diagnostics, and
preserve valid stored state.

------------------------------------------------------------------------

## 13. Technology stack

The following is the approved architecture baseline. Exact versions and
compatibility must be verified against the repository and deployment
environment before installation or upgrades.

  -----------------------------------------------------------------------
  Concern                 Baseline                Rule
  ----------------------- ----------------------- -----------------------
  Frontend                React + Vite +          Use for the student web
                          TypeScript              interface if the audit
                                                  confirms a separate
                                                  frontend is needed

  Routing                 React Router if         Do not add unnecessary
                          multiple page routes    routing complexity
                          are useful              

  Styling                 CSS modules or          Avoid a large design
                          lightweight CSS         system unless already
                                                  present or approved

  Backend                 Existing Python         Reuse existing logic;
                          educational logic;      do not duplicate
                          FastAPI adapter if      learning rules in
                          needed                  JavaScript

  Database                PostgreSQL as the       Preserve a working
                          proposed deployed       existing DB if
                          target                  adequate; audit before
                                                  migrating

  ORM/migrations          Existing approach;      Do not create a second
                          otherwise SQLAlchemy    migration system
                          2 + Alembic             

  API                     REST/JSON over HTTPS    Version public API
                                                  paths as `/api/v1`

  Voice                   ElevenLabs server-side  Verify current provider
                          API integration         API details and
                                                  credential availability

  Testing                 pytest;                 Reuse compatible
                          HTTPX/TestClient;       installed tools where
                          Vitest; React Testing   possible
                          Library; Playwright if  
                          useful                  

  Deployment              Static frontend +       Choose the smallest
                          Python backend +        viable deployment
                          managed PostgreSQL if   topology
                          selected                

  Monitoring              Structured logs,        Add external error
                          request IDs, health     monitoring only if
                          checks                  worthwhile and approved

  File storage            None for the initial    No confirmed upload
                          MVP                     requirement; do not add
                                                  object storage
                                                  preemptively
  -----------------------------------------------------------------------

### Trade-offs

-   React provides a flexible demo interface but requires a separate
    frontend build; preserve Streamlit as a backup.
-   Python reuse minimizes rewriting educational logic.
-   PostgreSQL supports relational integrity and concurrent sessions but
    may be unnecessary for a local-only prototype if a current database
    already meets the requirements.
-   A server-side ElevenLabs adapter protects credentials and allows
    reliable fallback.
-   Avoid microservices, Kubernetes, Redis, job queues, and complex
    state libraries unless a verified requirement demands them.

------------------------------------------------------------------------

## 14. System architecture

### Logical request flow

`Student browser → React frontend → REST API/backend → session and learning services → existing educational logic and persistence`

For external calls:

-   Tutoring service → verified AI/model provider, if the current tutor
    requires one.
-   Voice adapter → ElevenLabs service.
-   Provider calls must be bounded by timeouts and safe error handling.

### Backend modules

-   **Session service:** create, validate, expire, and revoke anonymous
    sessions.
-   **Assessment service:** fetch safe assessment content, create
    attempts, validate answers, score, and complete attempts.
-   **Content service:** serve published lessons and concept references.
-   **Tutoring service:** coordinate context, student reasoning,
    teaching, and follow-up.
-   **Misconception service:** store evidence-based hypotheses and state
    transitions.
-   **Progress service:** calculate assessment comparisons and session
    summary.
-   **Voice adapter:** invoke ElevenLabs and record sanitized
    operational outcomes.
-   **Persistence layer:** queries, transactions, and data mapping.
-   **Routes/controllers:** HTTP validation, status codes, and service
    invocation.

Keep these modules lightweight. If the current repository has a good
equivalent structure, map it to these responsibilities instead of
recreating it.

### Architecture constraints

-   Educational business logic must have one authoritative
    implementation.
-   Routes should not contain complex scoring or misconception
    inference.
-   Frontend components must not access the database directly.
-   Secrets must not be embedded in frontend environment variables that
    are bundled into public JavaScript.
-   Streamlit must remain independently runnable if it exists.
-   Do not assume the Streamlit app and new API can safely share a
    database until schema and concurrent access are verified.

------------------------------------------------------------------------

## 15. Project folder structure

This is a **proposed target structure**, not a claim about the current
repository. First inspect the real tree and preserve existing naming and
useful files. Adapt the structure incrementally rather than moving the
whole project without need.

``` text
learnloop-ai/
├── context.md
├── README.md
├── .gitignore
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── er-diagram.mmd
│   ├── assessment-audit.md
│   └── decisions.md
├── frontend/                    # If React app is not already elsewhere
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   ├── routes/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── session/
│   │   │   ├── assessment/
│   │   │   ├── lesson/
│   │   │   ├── tutor/
│   │   │   ├── voice/
│   │   │   └── progress/
│   │   ├── lib/
│   │   │   └── api-client.ts
│   │   └── styles/
│   └── tests/
├── backend/                     # Only if a separate package is appropriate
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── integrations/
│   │   │   └── elevenlabs.py
│   │   ├── db/
│   │   └── core/
│   └── tests/
├── migrations/                  # Use the selected migration system's layout
└── existing-streamlit-files/    # Preserve actual existing location; do not rename blindly
```

Do not create empty directories just to match this diagram. Let the
verified codebase and approved module boundaries determine the final
layout.

------------------------------------------------------------------------

## 16. Database entities

The proposed relational model includes:

1.  `learning_sessions` --- anonymous session identity and lifecycle.
2.  `concepts` --- fraction concepts and their stable codes.
3.  `lessons` --- lesson content and publication status.
4.  `lesson_concepts` --- many-to-many lesson/concept mapping.
5.  `questions` --- question prompts and type.
6.  `question_options` --- answer choices and internal correctness
    flags.
7.  `question_concepts` --- many-to-many question/concept mapping.
8.  `assessments` --- assessment identity and version.
9.  `assessment_questions` --- ordered membership and points possible.
10. `assessment_attempts` --- a session's attempt at an assessment.
11. `answer_submissions` --- answer for a question in an attempt.
12. `reasoning_responses` --- one or more explanations linked to an
    answer.
13. `tutoring_interactions` --- ordered conversation/tutoring events.
14. `misconception_hypotheses` --- tentative learning difficulties and
    evidence.
15. `voice_events` --- voice provider outcomes and operational metadata.

A separate `progress_reports` table is not required initially because
reports can be calculated from attempts, answers, concepts, and tutoring
evidence. Add one only if immutable report snapshots become a real
requirement.

------------------------------------------------------------------------

## 17. Relational schema

The following is a schema reference. It must be reconciled with existing
repository models before use as a migration. PostgreSQL-specific types
and functions are used.

``` sql
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'expired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ
);

CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'archived')),
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE lesson_concepts (
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE RESTRICT,
    PRIMARY KEY (lesson_id, concept_id)
);

CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE,
    prompt TEXT NOT NULL,
    question_type TEXT NOT NULL
        CHECK (question_type IN ('multiple_choice', 'short_text')),
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'archived')),
    explanation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE question_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    option_key TEXT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (question_id, option_key),
    UNIQUE (question_id, id)
);

CREATE TABLE question_concepts (
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE RESTRICT,
    PRIMARY KEY (question_id, concept_id)
);

CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL
        CHECK (assessment_type IN ('pre', 'post', 'practice')),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (code, version)
);

CREATE TABLE assessment_questions (
    assessment_id UUID NOT NULL
        REFERENCES assessments(id) ON DELETE RESTRICT,
    question_id UUID NOT NULL
        REFERENCES questions(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK (position > 0),
    points_possible NUMERIC(7,2) NOT NULL DEFAULT 1
        CHECK (points_possible > 0),
    PRIMARY KEY (assessment_id, question_id),
    UNIQUE (assessment_id, position)
);

CREATE TABLE assessment_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES learning_sessions(id) ON DELETE RESTRICT,
    assessment_id UUID NOT NULL
        REFERENCES assessments(id) ON DELETE RESTRICT,
    attempt_no INTEGER NOT NULL CHECK (attempt_no > 0),
    status TEXT NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    raw_score NUMERIC(9,2),
    max_score NUMERIC(9,2),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE (session_id, assessment_id, attempt_no),
    CHECK (
        (status = 'completed'
         AND completed_at IS NOT NULL
         AND raw_score IS NOT NULL
         AND max_score IS NOT NULL
         AND raw_score >= 0
         AND max_score > 0
         AND raw_score <= max_score)
        OR
        (status <> 'completed' AND completed_at IS NULL)
    )
);

CREATE TABLE answer_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL
        REFERENCES assessment_attempts(id) ON DELETE RESTRICT,
    question_id UUID NOT NULL,
    selected_option_id UUID,
    answer_text TEXT,
    is_correct BOOLEAN,
    points_awarded NUMERIC(7,2),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (attempt_id, question_id),
    FOREIGN KEY (question_id)
        REFERENCES questions(id) ON DELETE RESTRICT,
    FOREIGN KEY (question_id, selected_option_id)
        REFERENCES question_options(question_id, id)
        ON DELETE RESTRICT,
    CHECK (selected_option_id IS NOT NULL OR answer_text IS NOT NULL),
    CHECK (points_awarded IS NULL OR points_awarded >= 0)
);

CREATE TABLE reasoning_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_submission_id UUID NOT NULL
        REFERENCES answer_submissions(id) ON DELETE RESTRICT,
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    response_text TEXT NOT NULL,
    input_mode TEXT NOT NULL
        CHECK (input_mode IN ('text', 'speech_transcript')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (answer_submission_id, sequence_no)
);

CREATE TABLE tutoring_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES learning_sessions(id) ON DELETE RESTRICT,
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    role TEXT NOT NULL CHECK (role IN ('student', 'tutor', 'system')),
    interaction_type TEXT NOT NULL
        CHECK (interaction_type IN (
            'question', 'reasoning_prompt', 'reasoning_response',
            'explanation', 'feedback', 'clarification',
            'teach_back', 'practice_feedback', 'system_event'
        )),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, sequence_no)
);

CREATE TABLE misconception_hypotheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES learning_sessions(id) ON DELETE RESTRICT,
    concept_id UUID REFERENCES concepts(id) ON DELETE RESTRICT,
    evidence_answer_id UUID
        REFERENCES answer_submissions(id) ON DELETE RESTRICT,
    code TEXT NOT NULL,
    description TEXT NOT NULL,
    confidence NUMERIC(4,3)
        CHECK (confidence >= 0 AND confidence <= 1),
    status TEXT NOT NULL DEFAULT 'tentative'
        CHECK (status IN ('tentative', 'confirmed', 'resolved', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE voice_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES learning_sessions(id) ON DELETE RESTRICT,
    interaction_id UUID
        REFERENCES tutoring_interactions(id) ON DELETE SET NULL,
    provider TEXT NOT NULL CHECK (provider = 'elevenlabs'),
    direction TEXT NOT NULL
        CHECK (direction IN ('text_to_speech', 'speech_to_text')),
    status TEXT NOT NULL
        CHECK (status IN ('requested', 'succeeded', 'failed', 'cancelled')),
    duration_ms INTEGER CHECK (duration_ms >= 0),
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_sessions_expiry
    ON learning_sessions (expires_at);
CREATE INDEX idx_attempts_session_started
    ON assessment_attempts (session_id, started_at DESC);
CREATE INDEX idx_attempts_assessment_status
    ON assessment_attempts (assessment_id, status);
CREATE INDEX idx_answers_attempt
    ON answer_submissions (attempt_id);
CREATE INDEX idx_reasoning_answer
    ON reasoning_responses (answer_submission_id);
CREATE INDEX idx_interactions_session
    ON tutoring_interactions (session_id, sequence_no);
CREATE INDEX idx_misconceptions_session_status
    ON misconception_hypotheses (session_id, status);
CREATE INDEX idx_voice_events_session
    ON voice_events (session_id, created_at DESC);
```

### Schema cautions

-   `gen_random_uuid()` availability depends on the PostgreSQL
    version/extensions. Verify it in the target environment.
-   The schema intentionally enforces
    `answer_submissions.question_id → questions.id` as a foreign key.
    The cross-table rule that the question must also belong to the
    assessment referenced by the answer's attempt must be validated by
    the assessment service inside the same database transaction. This
    avoids storing a redundant `assessment_id` on each answer solely to
    construct a composite foreign key. If the repository's verified data
    model supports a cleaner declarative constraint without redundant
    data, document and test that alternative.
-   The schema is a proposed baseline, not a migration to run blindly
    against existing data. Validate the DDL in a disposable PostgreSQL
    database and run integrity tests before adopting it.
-   Ensure `updated_at` is maintained by application code or a database
    trigger.
-   Use transactions to prevent answer submission after attempt
    completion and to enforce required-question completion.
-   Published assessment definitions should be immutable; changes create
    a new version.
-   Do not expose `is_correct` in public question payloads.
-   Deletion must follow an explicit retention policy. Do not use broad
    cascading deletion for historical attempts and answers.
-   Validate all score bounds against the selected assessment's points
    possible, not only the simple `raw_score <= max_score` check.

------------------------------------------------------------------------

## 18. ER diagram reference

The canonical source path for the diagram is:

**`docs/er-diagram.mmd`**

Keep that Mermaid ER source synchronized with the final relational
schema and include it in version control. If it does not yet exist,
create it only during the approved implementation/documentation phase.

The diagram must include all actual tables, PK/FK markers,
cardinalities, and optionality. It must not depict a relationship that
is not represented by a foreign key or documented logical rule.

The ER source should be rendered and reviewed as part of the schema
review. The diagram in this file is a reference, not a substitute for a
validated standalone ERD.

------------------------------------------------------------------------

## 19. Primary keys, foreign keys, candidate keys, and constraints

### Key strategy

-   Primary keys: UUIDs for durable entities.
-   Candidate/alternate keys: stable `code` values for concepts,
    lessons, assessments, and optionally questions.
-   Session secret: unique token hash, not a user-supplied identifier.
-   Junction-table composite keys: `(lesson_id, concept_id)`,
    `(question_id, concept_id)`, and `(assessment_id, question_id)`.
-   Ordered uniqueness: `(assessment_id, position)` and
    `(session_id, sequence_no)` where specified.
-   Attempt uniqueness: `(session_id, assessment_id, attempt_no)`.
-   Answer uniqueness: one answer per question per attempt unless an
    explicit product rule permits answer revisions. Reasoning
    clarifications are stored separately.

### Status fields

-   Session: `active → completed` or `active → expired`; terminal-state
    behavior must be defined and tested.
-   Attempt: `in_progress → completed` or `in_progress → abandoned`;
    completed/abandoned attempts are not reopened.
-   Lesson/question: `draft → published → archived` according to
    content-management rules. The MVP may seed content without building
    an admin UI.
-   Misconception hypothesis: `tentative → confirmed`, `resolved`, or
    `rejected`; transition rules must be explicit in the service layer.
-   Voice event: `requested → succeeded`, `failed`, or `cancelled`.

### Deletion behavior

-   Historical session/attempt/answer records should not be cascaded
    away accidentally.
-   Content junction rows may cascade when deleting unused draft
    content.
-   Referenced published content should be restricted from deletion or
    archived instead.
-   Voice interaction links may be set to null if the interaction is
    removed under an approved cleanup process.
-   Expired session cleanup must explicitly handle dependent records in
    a transaction or safe ordered job.
-   The exact retention duration remains unresolved.

### Indexing

Use the indexes in the schema as starting points. Add indexes only for
measured query patterns. Foreign-key columns used for lookups and
cleanup should be indexed where PostgreSQL does not already have a
suitable index. Avoid speculative indexes on every field.

------------------------------------------------------------------------

## 20. Normalization decisions

### Functional dependencies

Examples under the proposed keys:

-   `learning_sessions.id → token_hash, status, created_at, expires_at`
-   `concepts.id → code, name, description`
-   `lessons.id → code, title, content, status, sequence_no`
-   `question_options.id → question_id, option_key, option_text, is_correct`
-   `(question_id, option_key) → option_text, is_correct`
-   `assessments.id → code, title, assessment_type, version, is_active`
-   `(assessment_id, question_id) → position, points_possible`
-   `(session_id, assessment_id, attempt_no) → attempt attributes`
-   `(attempt_id, question_id) → answer attributes`
-   `(answer_submission_id, sequence_no) → reasoning response`
-   `(session_id, sequence_no) → tutoring interaction`

### Normal-form goals

-   **1NF:** Store individual values; do not store lists of question
    IDs, options, or concepts in a text field.
-   **2NF:** Junction-table attributes depend on the entire composite
    key.
-   **3NF:** Keep session, lesson, question, attempt, answer, and
    concept attributes in their appropriate tables.
-   **BCNF:** Aim for BCNF where all determinants are candidate keys;
    verify after all functional dependencies and uniqueness rules are
    known.

### Deliberate snapshots

`raw_score` and `max_score` are stored on a completed attempt as
historical results. They are computed transactionally from answer-level
scoring and must be tested for consistency. Percentage is calculated
from these values rather than independently edited.

Misconception hypotheses are separate from answers because an
interpretation can evolve as evidence arrives. Progress reports are
derived and need not be persisted initially.

------------------------------------------------------------------------

## 21. Database migrations and seed strategy

1.  Audit the existing persistence system before creating migrations.
2.  Back up existing data and preserve the Streamlit app.
3.  Choose exactly one migration tool. If no tool exists and SQLAlchemy
    is approved, use Alembic.
4.  Never run a destructive migration against the only copy of project
    data.
5.  Test migrations on a disposable local database.
6.  Use forward migrations; document rollback limits for data
    transformations.
7.  Seed only the minimum approved fraction concepts, lessons,
    assessment metadata, questions, and options.
8.  Do not seed guessed replacements for existing assessment questions.
9.  Keep seed scripts repeatable/idempotent where possible.
10. Separate development/test seed data from production data.
11. Never seed credentials or real student data.
12. Verify schema constraints, foreign keys, indexes, and transaction
    behavior in tests.
13. Confirm that the Streamlit backup remains runnable after schema
    changes.
14. Keep assessment versions immutable after attempts use them.

------------------------------------------------------------------------

## 22. API endpoints and contracts

Base path: `/api/v1`. All private endpoints require a valid anonymous
session mechanism. Use HTTPS in deployed environments. Use JSON except
for a verified audio upload/response contract.

### Endpoint inventory

  --------------------------------------------------------------------------------
  Method             Endpoint                                   Purpose
  ------------------ ------------------------------------------ ------------------
  POST               `/api/v1/sessions`                         Create anonymous
                                                                session

  GET                `/api/v1/sessions/current`                 Retrieve current
                                                                session state

  DELETE             `/api/v1/sessions/current`                 End session /
                                                                initiate approved
                                                                cleanup

  GET                `/api/v1/lessons`                          List published
                                                                lessons

  GET                `/api/v1/lessons/{lesson_id}`              Fetch lesson

  GET                `/api/v1/assessments/{code}`               Fetch safe
                                                                assessment
                                                                definition

  POST               `/api/v1/assessments/{code}/attempts`      Start attempt

  GET                `/api/v1/attempts/{attempt_id}`            Read attempt
                                                                status

  POST               `/api/v1/attempts/{attempt_id}/answers`    Submit answer

  POST               `/api/v1/answers/{answer_id}/reasoning`    Submit reasoning

  POST               `/api/v1/tutor/messages`                   Send tutoring
                                                                message

  POST               `/api/v1/tutor/teach-back`                 Submit teach-back
                                                                response

  POST               `/api/v1/attempts/{attempt_id}/complete`   Complete attempt

  GET                `/api/v1/progress`                         Retrieve session
                                                                progress

  POST               `/api/v1/voice/synthesize`                 Request spoken
                                                                tutor output

  POST               `/api/v1/voice/transcribe`                 Optional
                                                                transcription
                                                                endpoint, only if
                                                                approved and
                                                                supported

  GET                `/api/v1/health`                           Sanitized health
                                                                status
  --------------------------------------------------------------------------------

### Session creation

`POST /api/v1/sessions`

Request: `{}`

Response example:

``` json
{
  "session": {
    "id": "uuid",
    "status": "active",
    "expires_at": "2026-10-11T18:00:00Z"
  }
}
```

The actual session secret must be issued through the secure session
mechanism, not exposed in normal JSON by default.

### Assessment retrieval

`GET /api/v1/assessments/{code}`

Return assessment title/version and ordered question prompts/options.
Never include answer keys or private scoring logic in the public
payload.

### Start an attempt

`POST /api/v1/assessments/{code}/attempts`

Request may contain an approved version identifier if the policy
requires it; otherwise the backend chooses the active version. The
backend creates a new `attempt_no` atomically.

### Submit an answer

`POST /api/v1/attempts/{attempt_id}/answers`

Example request:

``` json
{
  "question_id": "uuid",
  "selected_option_id": "uuid"
}
```

For short text questions, use a validated `answer_text` field. Reject
requests with neither a valid option nor text. Do not accept
client-provided `is_correct`, score, mastery, or assessment ownership.

### Submit reasoning

`POST /api/v1/answers/{answer_id}/reasoning`

Example request:

``` json
{
  "response_text": "I thought the larger denominator meant the larger fraction.",
  "input_mode": "text"
}
```

For speech-derived text, `input_mode` may be `speech_transcript` only
when the transcription workflow is approved.

### Tutor message

`POST /api/v1/tutor/messages`

Example request:

``` json
{
  "message": "I don't understand why one-third is smaller.",
  "context": {
    "lesson_id": "uuid",
    "question_id": "uuid"
  }
}
```

The backend validates ownership and context. It returns tutor text and,
where appropriate, a follow-up question. It must not trust
client-supplied assessment results or misconception labels.

### Complete attempt

`POST /api/v1/attempts/{attempt_id}/complete`

Request: `{}`

The backend validates required answers and allowed state transition,
computes final score, and commits atomically. Repeated completion must
not double-score or mutate the completed result.

### Progress

`GET /api/v1/progress`

Return recorded pre/post scores, maximum scores, comparable
percentage-point change when valid, evidence-backed concept summaries,
and review tasks. If a valid comparison cannot be calculated, state that
it is unavailable rather than fabricating it.

### Voice synthesis

`POST /api/v1/voice/synthesize`

The final body/response format must be chosen only after verifying the
current ElevenLabs API and intended audio delivery method. Do not invent
voice IDs, model IDs, endpoint URLs, or response payloads. Keep provider
credentials on the backend and enforce text length, timeout, and rate
limits.

### Error contract

Use a consistent error object:

``` json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The submitted answer is invalid.",
    "details": []
  }
}
```

Recommended HTTP statuses:

-   `400`: invalid workflow operation or malformed request.
-   `401`: missing, invalid, or expired session.
-   `403`: valid session but disallowed operation.
-   `404`: resource does not exist or is not visible to this session.
-   `409`: duplicate/conflicting state transition.
-   `422`: schema or field validation failure.
-   `429`: rate limit exceeded.
-   `500`: unexpected internal error.
-   `502`/`503`: upstream AI/voice provider unavailable.

Use pagination only where collection size warrants it. The initial
assessment question list should be ordered and returned as a whole.

------------------------------------------------------------------------

## 23. Frontend routes and page requirements

The routes below are proposed logical routes. Do not put the secret
session token in the URL. Resource IDs in URLs do not grant
authorization.

  ---------------------------------------------------------------------------
  Route                             Page                 Requirements
  --------------------------------- -------------------- --------------------
  `/`                               Welcome              Explain the learning
                                                         session and start
                                                         anonymously

  `/session/:id/assessment/pre`     Pre-assessment       Questions, answer
                                                         selection, progress,
                                                         submit states

  `/session/:id/lesson/:lessonId`   Lesson               Concept explanation,
                                                         examples, fraction
                                                         visuals

  `/session/:id/tutor`              Tutor                Conversation,
                                                         reasoning prompt,
                                                         text entry,
                                                         feedback, voice
                                                         controls

  `/session/:id/practice`           Practice             Targeted question
                                                         and response
                                                         feedback

  `/session/:id/assessment/post`    Post-assessment      Separate post-test
                                                         workflow

  `/session/:id/progress`           Progress report      Scores, valid
                                                         comparison,
                                                         evidence-backed
                                                         summary
  ---------------------------------------------------------------------------

### Reusable components

-   `AppLayout`
-   `LearningProgress`
-   `FractionVisual`
-   `QuestionCard`
-   `AnswerOption`
-   `AssessmentNavigation`
-   `TutorMessage`
-   `ReasoningPrompt`
-   `MisconceptionFeedback`
-   `PracticeQuestion`
-   `VoiceControls`
-   `ProgressSummary`
-   `LoadingState`
-   `EmptyState`
-   `ErrorState`

### State and API integration

-   Use local component state for transient inputs.
-   Use a small session-level provider/store only for shared
    session/workflow state.
-   Centralize HTTP requests and error parsing in an API client.
-   Add a query/cache library only if it materially helps.
-   Keep scoring, assessment rules, and misconception logic on the
    backend.
-   Include loading, empty, success, validation, network, and
    voice-failure states.
-   Do not show success until the backend confirms it.

------------------------------------------------------------------------

## 24. UI/UX design direction

-   Calm, clear, student-friendly interface.
-   One primary action per step.
-   Short explanations and worked examples.
-   Fraction visuals should represent the actual mathematical concept,
    not merely decorate the page.
-   Keep the current question and progress visible during assessments.
-   Make tutor responses easy to distinguish from student responses.
-   Ask for reasoning in a non-judgmental way.
-   Present a misconception as a possible misunderstanding, not a label
    applied to the student.
-   Voice playback must have accessible text and visible playback/error
    state.
-   Voice is an enhancement to the same learning flow; text remains
    available.
-   Support keyboard navigation, visible focus, semantic headings,
    readable contrast, and clear button labels.
-   Design for common laptop and mobile viewport widths.
-   Do not add gamification, complex dashboards, or animation that
    distracts from the demo's core learning loop.

------------------------------------------------------------------------

## 25. Authentication and authorization

There is no account-based authentication in the MVP. Anonymous session
authorization is required.

-   Generate a high-entropy cryptographically secure token.
-   Store a cryptographic hash, not the raw token.
-   Use HTTPS in deployment.
-   Prefer Secure, HttpOnly, appropriately configured SameSite cookies
    when compatible with the deployment topology.
-   Avoid tokens in URLs, logs, analytics, or frontend bundles.
-   Validate session state and expiry for every private API operation.
-   Check resource ownership on every attempt, answer, reasoning,
    tutoring, and progress endpoint.
-   Return a consistent unauthorized/not-found response without leaking
    another session's records.
-   Protect cookie-authenticated state-changing routes against CSRF as
    appropriate.
-   Restrict CORS to known frontend origins.
-   Do not add user login or admin roles without explicit approval.

------------------------------------------------------------------------

## 26. Security requirements

-   Validate request shape, lengths, allowed values, and resource
    relationships on the backend.
-   Use parameterized database queries/ORM APIs.
-   Enforce constraints and transactions for state-changing operations.
-   Never trust browser-submitted scores, correctness, role, or mastery
    values.
-   Keep ElevenLabs and any AI provider secrets server-side.
-   Keep secret files out of Git; commit only `.env.example` with
    placeholder values.
-   Limit request sizes and rate for AI/voice endpoints.
-   Apply timeouts and bounded retries to provider calls.
-   Render AI-generated content safely; do not treat it as trusted HTML.
-   Treat student input as untrusted prompt content and constrain tutor
    scope to the educational task.
-   Do not log raw audio, session secrets, provider keys, or unnecessary
    student content.
-   Avoid collecting names or personal data that the product does not
    need.
-   Do not store raw audio by default.
-   Provide a text fallback for voice failure.
-   Add tests for cross-session access and concurrent submissions.

------------------------------------------------------------------------

## 27. File storage requirements

No user-uploaded files are required for the MVP. Do not introduce object
storage merely for architectural completeness.

Voice synthesis may return an audio payload or a temporary playback
reference depending on the verified ElevenLabs integration. Choose the
simplest secure mechanism supported by the actual API. Avoid persistent
audio storage unless the owner approves a concrete need and retention
policy.

If a future feature introduces uploads, define file types, size limits,
access control, retention, and deletion before implementing it.

------------------------------------------------------------------------

## 28. Error handling

### User-facing behavior

-   Explain what the student can do next.
-   Keep errors concise and non-technical.
-   Offer retry when safe.
-   Preserve already recorded answers.
-   Distinguish a voice failure from a tutoring failure.
-   Provide text interaction if voice is unavailable.
-   Do not expose stack traces, SQL errors, internal paths, or provider
    credentials.

### Backend behavior

-   Use consistent error codes and HTTP statuses.
-   Log sanitized diagnostics with a request/correlation ID.
-   Roll back failed multi-step database operations.
-   Make answer submission and attempt completion idempotent or return a
    documented conflict.
-   Use provider timeouts and bounded retry policies.
-   Do not retry non-idempotent operations without an idempotency
    strategy.
-   Return only safe, minimal error details to the client.

------------------------------------------------------------------------

## 29. Testing requirements

### Backend unit tests

Test: - Existing assessment scoring rules. - Attempt state
transitions. - Question/option membership validation. - Duplicate answer
prevention. - Reasoning association. - Misconception status transitions
and confidence bounds. - Progress calculations. - Session expiry and
ownership. - Provider timeout and failure handling.

### API integration tests

Test: - Session creation and expiry. - Cross-session access rejection. -
Assessment retrieval without answer-key leakage. - Attempt creation and
numbering. - Answer submission and duplicate requests. - Completion and
scoring transaction. - Post-assessment and progress. - Voice success,
invalid credentials, timeout, and fallback behavior. - Database rollback
on failure.

### Frontend tests

Test: - Session initialization. - Question navigation and answer
selection. - Loading, validation, success, and error states. - Reasoning
input. - Tutor and practice interactions. - Voice controls and
fallback. - Progress report. - Keyboard and accessible-label behavior.

### End-to-end tests

The critical journey is:

1.  Start an anonymous session.
2.  Complete the pre-assessment.
3.  Open a fraction lesson.
4.  Answer a question incorrectly.
5.  Explain the reasoning.
6.  Receive targeted feedback.
7.  Complete a follow-up practice question.
8.  Complete the post-assessment.
9.  View the progress report.
10. Complete a meaningful ElevenLabs spoken tutor interaction.
11. Verify that text tutoring still works after voice failure.

### Concurrency/integrity tests

-   Rapid duplicate answer submission.
-   Duplicate attempt completion.
-   Concurrent requests on one attempt.
-   Expiry during a workflow.
-   Provider failure during tutoring.
-   Shared database access by Streamlit and the new application, if
    applicable.

Do not weaken existing tests simply to make a migration pass.

------------------------------------------------------------------------

## 30. Deployment architecture

Proposed deployed shape:

-   Static React frontend.
-   Python backend service.
-   Managed PostgreSQL if confirmed as the target database.
-   Server-side secret configuration.
-   HTTPS.
-   Sanitized health endpoint and structured logs.

Use the minimum deployment services needed for a successful demo. Do not
introduce Kubernetes, multiple backend services, message brokers, or
separate workers without a verified need.

### Health and monitoring

`GET /api/v1/health` should provide a sanitized health result. A
separate readiness check may verify database connectivity if needed. Do
not reveal credentials or internal topology.

Log request IDs, route/status, latency, sanitized error category, and
voice-provider outcome/duration. Avoid logging tokens, raw audio, and
unnecessary conversation content.

The exact hosting provider, deployment URL, database host, and budget
have not been specified. Do not invent them.

------------------------------------------------------------------------

## 31. Environment variables

Create `.env.example` with names and placeholder values only. Never
commit real secrets.

Candidate variables, to be finalized after the repository audit:

``` dotenv
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173

# Configure only if PostgreSQL is selected.
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME

# Generate a strong random value; never use this placeholder in deployment.
SESSION_TOKEN_PEPPER=replace-with-a-strong-random-secret

# Required for the live demo; obtain from the project owner/provider account.
ELEVENLABS_API_KEY=
# Provider-specific voice/model settings must be verified before use.
ELEVENLABS_VOICE_ID=
ELEVENLABS_MODEL_ID=

# Configure only if the verified tutor implementation requires an AI provider.
AI_PROVIDER_API_KEY=
```

Rules:

-   Do not assume every variable is needed; remove unused settings.
-   Never invent a voice ID, model ID, API endpoint, or API key.
-   Keep backend secrets out of `VITE_*` frontend variables, because
    Vite exposes those to browser code.
-   Validate required configuration at startup and fail with a clear,
    secret-safe message.
-   Document which variables are required locally versus only in
    deployment.
-   If the existing application uses different environment names,
    document and preserve them where practical.

------------------------------------------------------------------------

## 32. Git workflow

Before making changes:

1.  Inspect `git status`, current branch, remotes, recent commits, and
    tracked/untracked files.
2.  Identify existing uncommitted work and do not overwrite or discard
    it.
3.  Locate and verify the Streamlit backup.
4.  Read project instructions, README, dependency files, and test
    commands.
5.  Record the repository audit before large changes.

During implementation, after approval:

-   Work in small, coherent increments.
-   Run relevant tests before committing.
-   Keep secrets, `.env` files, databases, caches, and build outputs out
    of Git.
-   Do not use destructive reset, clean, force-push, or history-rewrite
    commands without explicit authorization.
-   Review the diff before each commit.
-   Use meaningful commit messages.
-   Push only to the verified intended remote/branch and only when
    authorized.
-   Report test, commit, and push status accurately; never claim an
    operation succeeded without verification.

------------------------------------------------------------------------

## 33. Documentation requirements

Maintain:

-   `README.md`: prerequisites, installation, local run commands, test
    commands, and demo flow.
-   `context.md`: master product/architecture constraints.
-   `docs/architecture.md`: verified component diagram and module
    responsibilities.
-   `docs/api.md`: actual endpoint contracts and error model.
-   `docs/database.md`: final schema, migration, constraints, and
    retention behavior.
-   `docs/er-diagram.mmd`: canonical ER diagram source.
-   `docs/assessment-audit.md`: current assessment
    questions/scoring/tests and approved disposition.
-   `docs/decisions.md`: decisions, rationale, date, and unresolved
    items.

Documentation must describe the actual implemented state. Mark proposed
or deferred functionality clearly.

------------------------------------------------------------------------

## 34. Implementation phases

Do not start implementation until the project owner has authorized it.
Once authorized, use this sequence:

### Phase 0 --- Repository audit

-   Inspect the actual working tree, Git state, entry points,
    dependencies, tests, educational logic, assessment, persistence, and
    Streamlit backup.
-   Identify existing architecture and actual behavior.
-   Record assessment findings and incompatibilities.
-   Do not modify application code during an audit-only phase unless
    explicitly approved.

### Phase 1 --- Architecture reconciliation

-   Compare actual code with this specification.
-   Confirm whether FastAPI, PostgreSQL, SQLAlchemy, and Alembic are
    necessary.
-   Resolve the assessment policy using repository evidence.
-   Verify ElevenLabs capabilities and credential availability.
-   Update the architecture/schema proposal and obtain approval for any
    material deviation.

### Phase 2 --- Data/API foundation

-   Finalize schema and ER diagram.
-   Validate PostgreSQL DDL in a disposable database if PostgreSQL is
    selected.
-   Establish migration and seed strategy.
-   Implement session authorization and API contracts.
-   Add tests for data integrity and cross-session access.

### Phase 3 --- Frontend foundation

-   Establish or adapt the React/Vite/TypeScript frontend.
-   Implement the session flow and reusable UI states.
-   Centralize API integration.
-   Preserve the Streamlit backup.

### Phase 4 --- Core learning loop

-   Connect assessment, lessons, reasoning capture, tutoring, targeted
    practice, post-assessment, and progress report.
-   Use the verified educational engine as the source of truth.
-   Test the complete learning path.

### Phase 5 --- ElevenLabs demo path

-   Implement spoken tutor output using verified provider documentation
    and owner-supplied credentials.
-   Test success, timeout, invalid credentials, and text fallback.
-   Rehearse the actual demo path.

### Phase 6 --- Verification and delivery

-   Run unit, integration, frontend, and end-to-end tests.
-   Review accessibility, production build, configuration, and privacy.
-   Verify the Streamlit backup remains runnable.
-   Update documentation and report exactly what passed, failed, or
    remains unresolved.

------------------------------------------------------------------------

## 35. Acceptance criteria

The MVP is acceptable when:

-   [ ] A learner starts without registration.
-   [ ] A unique anonymous session is created and validated.
-   [ ] Session data cannot be accessed by another session.
-   [ ] The approved fractions pre-assessment can be completed and
    scored.
-   [ ] Existing assessment behavior was inspected before being changed.
-   [ ] The student can access fraction teaching content.
-   [ ] The tutor can ask for reasoning and record the response.
-   [ ] Feedback is connected to the answer and reasoning evidence.
-   [ ] At least one targeted follow-up practice question works.
-   [ ] The post-assessment records a separate result.
-   [ ] The report shows only supported results and valid comparisons.
-   [ ] The live demo includes a successful, meaningful ElevenLabs
    spoken interaction.
-   [ ] Text-based tutoring remains usable if voice fails.
-   [ ] Provider credentials are not exposed to the browser or logs.
-   [ ] Duplicate submissions and completion requests do not corrupt
    results.
-   [ ] Relevant tests pass and existing tests are preserved.
-   [ ] The Streamlit backup remains runnable if present.
-   [ ] README and architecture/API/database/ERD documentation match the
    actual implementation.

------------------------------------------------------------------------

## 36. Definition of done

A task is done only when:

1.  The code implements the approved requirement.
2.  Existing useful behavior is preserved.
3.  Relevant tests are added or updated and run.
4.  Error and loading states are handled.
5.  Data integrity and session ownership are verified where applicable.
6.  No secrets are committed.
7.  Documentation is updated.
8.  The change is reviewed for unintended scope expansion.
9.  The agent reports actual verification results without exaggeration.

The MVP is demo-ready only when the end-to-end learning loop works and
the ElevenLabs voice moment has been tested in the intended environment.

------------------------------------------------------------------------

## 37. Known limitations and unresolved decisions

The following must remain visible until resolved; do not silently fill
the gaps.

1.  **Repository state:** Actual files, branch, tests, dependencies,
    entry points, and Git status must be inspected.
2.  **Assessment policy:** Inspect the existing
    assessment/questions/scoring before deciding to preserve, adapt, or
    replace them.
3.  **Database choice:** PostgreSQL is the proposed deployed target, but
    an existing suitable database may be retained after audit.
4.  **Backend boundary:** Whether to add FastAPI or adapt an existing
    Python interface depends on repository structure.
5.  **Schema validation:** The proposed schema is a design reference and
    requires relational validation before migrations. In particular, the
    question-to-attempt assessment membership must be enforced
    transactionally and covered by tests.
6.  **Session recovery:** Refresh/resume behavior and exact expiry
    duration require confirmation.
7.  **Data retention/deletion:** Retention period, cleanup behavior, and
    deletion guarantees are unresolved.
8.  **ElevenLabs configuration:** API key, voice ID, model ID, supported
    endpoints, output format, and quotas must come from verified
    provider documentation and owner-controlled configuration.
9.  **Speech input:** Student speech-to-text is optional until
    confirmed; spoken tutor output is the required live-demo capability.
10. **AI provider:** The specific tutoring model/provider is not
    specified by this file. Inspect the current implementation and
    obtain approval before adding a new provider.
11. **Mastery criteria:** Do not claim mastery until an explicit rule is
    defined.
12. **Assessment comparability:** Confirm whether pre/post assessments
    are comparable before reporting improvement.
13. **Hosting:** Provider, deployment URLs, and budget are not
    specified.
14. **Syllabus mapping:** No formal syllabus or rubric has been
    supplied.
15. **Performance targets:** Numeric latency, throughput, and
    availability targets are not specified.
16. **Architecture changes:** Any material deviation from this approved
    baseline must be documented and approved before implementation.

### Mandatory coding-agent guardrails

-   Do not begin coding merely because this file exists; follow the
    project owner's explicit implementation authorization.
-   Do not claim planned functionality is implemented.
-   Do not invent credentials, external API capabilities, IDs, or
    deployment details.
-   Do not silently replace assessment questions or scoring.
-   Do not expose answer keys, session secrets, or provider keys.
-   Do not let one anonymous session read another's data.
-   Do not overwrite the Streamlit backup or discard uncommitted work.
-   Do not execute unvalidated schema migrations against the only copy
    of data.
-   Do not add infrastructure without a concrete requirement.
-   Do not mark a test, commit, push, or deployment successful unless
    verified.

------------------------------------------------------------------------

## 38. Handoff checklist

### Captured in this file

-   [x] Project overview and problem statement
-   [x] Objectives and target users
-   [x] Anonymous session identity and permissions
-   [x] Functional and non-functional requirements
-   [x] MVP scope and excluded features
-   [x] End-to-end workflows and business rules
-   [x] Edge cases
-   [x] Technology stack and trade-offs
-   [x] System architecture and module responsibilities
-   [x] Proposed folder structure
-   [x] Database entities and PostgreSQL schema reference
-   [x] Keys, constraints, indexes, and deletion guidance
-   [x] Normalization goals and deliberate snapshots
-   [x] Migration and seed strategy
-   [x] API endpoint inventory and representative contracts
-   [x] Frontend route map and page/component requirements
-   [x] UI/UX direction
-   [x] Anonymous-session authorization and security
-   [x] File-storage decision
-   [x] Error handling
-   [x] Testing strategy
-   [x] Deployment and environment-variable guidance
-   [x] Git workflow and documentation requirements
-   [x] Implementation phases, acceptance criteria, and definition of
    done
-   [x] Known limitations and coding-agent guardrails

### Still unresolved or requiring repository/provider verification

-   [ ] Inspect the actual repository and current Git state.
-   [ ] Locate and verify the Streamlit backup.
-   [ ] Audit current assessment questions, scoring rules, and tests.
-   [ ] Confirm assessment preservation/adaptation/replacement policy.
-   [ ] Validate and reconcile the relational schema and composite
    foreign keys.
-   [ ] Confirm actual database and migration approach.
-   [ ] Confirm whether FastAPI is needed or an existing API layer
    should be reused.
-   [ ] Confirm session recovery, expiry, retention, and deletion
    policy.
-   [ ] Verify ElevenLabs API capabilities and configure valid
    owner-provided credentials.
-   [ ] Decide whether student speech-to-text is needed.
-   [ ] Confirm AI provider/model from the existing implementation or an
    approved decision.
-   [ ] Define mastery criteria and pre/post comparability.
-   [ ] Confirm hosting provider, deployment topology, and numeric
    performance targets.
-   [ ] Create and validate the standalone `docs/er-diagram.mmd`
    artifact.
-   [ ] Obtain explicit authorization before implementation begins.

**Final instruction to the coding agent:** Start with a read-only
repository audit and report findings. Do not begin implementation until
the owner explicitly authorizes it and the unresolved
architecture/schema issues that affect implementation have been
reconciled.
