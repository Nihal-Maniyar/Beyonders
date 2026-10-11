# LearnLoop AI — Antigravity Workspace Rules

> **Primary Contract:** All implementation must adhere strictly to `context.md` (v1.0) and the approved implementation plan.

---

## 1. Architecture and Project Structure
- **Deterministic Educational Engine Authority:** All scoring, misconception diagnosis (M1–M4, S1, U1), mastery criteria, and teach-back rubric evaluations are defined authoritatively in Python (`src/learnloop/domain/`). Never duplicate, re-implement, or alter these educational rules in client-side TypeScript.
- **Service & Persistence Boundaries:** Routes in `src/learnloop/api/v1/` must remain lightweight adapters. Business rules belong in `services/` and `domain/`. Database queries belong in models/repositories. Frontend components must never access persistence directly.
- **Streamlit Backup Preservation:** `app.py` is an independent live-demo fallback. New API models, schemas, or database modifications must not break `app.py` execution.
- **No Unapproved Infrastructure:** Do not introduce Redis, Celery/message brokers, Docker Swarm/Kubernetes, user auth tables, or file upload storage. Keep the architecture lightweight and verifiable.

---

## 2. Coding Standards
- **Python (Backend):**
  - Python >= 3.11 (Runtime: 3.13.5).
  - Type annotations required on all function signatures and service methods.
  - Pydantic models (v2) for all API request/response contracts and data schemas.
  - SQLAlchemy 2 style (`select(...)`, declarative mapping with `Mapped` and `mapped_column` or `Column`).
  - Code formatting: Ruff (line length 100, rules E, F, W, I).
- **TypeScript & React (Frontend):**
  - TypeScript strict mode enabled (`noImplicitAny: true`).
  - React 18 functional components with typed props and hooks.
  - No untyped `any` or ignored lint warnings.
  - Centralize HTTP calls in `src/services/api-client.ts`. Do not scatter `fetch()` calls across UI components.
  - Handle all UI states explicitly: `loading`, `empty`, `success`, `validation_error`, `network_error`, and `voice_fallback`.

---

## 3. Database Integrity & Dialect Compatibility
- **15 Relational Entities:** Schema must implement the 15 entities defined in `context.md` Section 16–20: `learning_sessions`, `concepts`, `lessons`, `lesson_concepts`, `questions`, `question_options`, `question_concepts`, `assessments`, `assessment_questions`, `assessment_attempts`, `answer_submissions`, `reasoning_responses`, `tutoring_interactions`, `misconception_hypotheses`, and `voice_events`.
- **Dialect Compatibility:** Support both SQLite (for zero-friction local testing) and PostgreSQL (deployed target) via SQLAlchemy 2 abstraction. Use `String(36)` / `UUID` compatibility for primary keys.
- **Transactional Atomicity:** Multi-step workflows (e.g., attempt completion, scoring calculation, misconception state transitions) must execute within an explicit database transaction with rollback on error.
- **Idempotency:** Rapid duplicate answer submissions or duplicate attempt completion calls must be idempotent and must never duplicate records or inflate scores.
- **Immutable Historical Records:** Never cascade-delete historical attempts, submitted answers, or reasoning records.

---

## 4. API Conventions (`/api/v1`)
- **Versioned Routes:** All endpoints must be prefixed with `/api/v1/`.
- **Standard Error Envelope:** All HTTP errors (4xx, 5xx) must return the uniform JSON structure:
  ```json
  {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "Human-readable non-technical explanation",
      "details": []
    }
  }
  ```
- **Standard Status Codes:**
  - `200 OK`: Successful read or update.
  - `201 Created`: Resource successfully created (e.g., new session, attempt).
  - `400 Bad Request`: Malformed payload or invalid workflow state.
  - `401 Unauthorized`: Missing, invalid, or expired session token.
  - `403 Forbidden`: Session does not own the requested resource.
  - `404 Not Found`: Resource does not exist.
  - `409 Conflict`: Conflict or duplicate attempt completion.
  - `422 Unprocessable Entity`: Validation failure.
  - `502 / 503 Upstream Error`: Upstream voice or AI provider failure.
- **Content Security:** `GET /api/v1/assessments/{code}` must return safe question prompts and options only; `is_correct` and answer keys must NEVER be included in public payloads.

---

## 5. Frontend Design & UI/UX Standards
- **Design Philosophy:** Calm, welcoming, distraction-free "learning studio" designed for learners studying basic fractions.
- **Interaction Clarity:** One clear primary action per screen. Visible progress stepper across the 6 learning stages.
- **Mathematical Accuracy:** Fraction visualizers (`FractionBar`, `FractionCompare`, `FractionExplorer`) must accurately represent unit parts, fair shares, and proportions.
- **Accessibility (a11y):**
  - Minimum WCAG 2.1 AA color contrast for all text and interactive badges.
  - Full keyboard navigability with visible focus outlines.
  - Semantic HTML (`<main>`, `<nav>`, `<header>`, `<article>`) and meaningful ARIA labels for fraction SVGs and audio controls.

---

## 6. Security and Privacy
- **Anonymous Sessions Only:** No student accounts, passwords, or persistent profiles.
- **Token Separation:** High-entropy secret token (generated server-side) must be separated from public `session.id`. Only a cryptographic hash (`token_hash`) is stored in the database.
- **Session Isolation:** Every private route must authenticate the session and verify that the target attempt, answer, reasoning, or interaction belongs strictly to that session.
- **Secret Isolation:** Provider credentials (`ELEVENLABS_API_KEY`, `SESSION_TOKEN_PEPPER`) must remain on the backend. Never prefix provider secrets with `VITE_` or expose them in client bundles.
- **Safe Rendering:** Sanitize all AI-generated or tutor text before rendering. Never treat student inputs or LLM responses as raw unescaped HTML.

---

## 7. ElevenLabs Voice & Fallback Discipline
- **Server-Side Proxy:** All voice synthesis requests go through `POST /api/v1/voice/synthesize`. The browser never calls ElevenLabs directly.
- **Bounded Timeouts:** Voice provider HTTP calls must enforce a strict timeout (max 5.0 seconds).
- **Graceful Fallback:** Voice failure, quota exhaustion, or missing credentials must never block or crash the learning flow. The interface must seamlessly display tutor text with an accessible fallback notice.
- **Operational Auditing:** Log every voice synthesis request, status (`requested`, `succeeded`, `failed`), latency (`duration_ms`), and sanitized error code in `voice_events`. Do not store raw audio binaries in the database.

---

## 8. Testing and Verification Discipline
- **Evidence-Based Reporting:** Never claim a feature is complete, working, or tested without executing verified tests and reporting real test outputs.
- **Test Matrix:**
  - Unit tests: verify all diagnosis rules (M1–M4, S1, U1) and scoring calculations (`pytest tests/unit`).
  - Integration tests: verify session isolation, transactional rollback, and API contracts (`pytest tests/api`, `pytest tests/integration`).
  - Frontend build: verify zero TypeScript or bundler errors (`npm run build`).
- **Preserve Existing Tests:** Never delete or weaken existing tests to force a migration to pass.

---

## 9. Git Safety & Documentation
- **Branch Isolation:** Perform all implementation work in the dedicated feature branch (`feature/learnloop-v1-foundation`). Do not commit to or merge into `main` without explicit user instruction.
- **No Secrets in VCS:** Never commit `.env`, API keys, tokens, or audio files. Commit only `.env.example`.
- **Synchronized Documentation:** Keep `docs/architecture.md`, `docs/api.md`, `docs/database.md`, and `docs/er-diagram.mmd` fully aligned with the running code.

