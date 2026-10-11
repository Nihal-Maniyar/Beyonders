# LearnLoop AI — Architecture Decision Records (ADRs)

> **Document Status:** Approved  
> **Source of Truth:** [`context.md`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/context.md)

---

## ADR-001: Anonymous Session Token Isolation
- **Context:** The system must protect student privacy and avoid managing persistent student accounts, passwords, or PII.
- **Decision:** Authenticate learners via high-entropy secret tokens (`ll_sec_...`). Return the secret token exactly once during session initialization (`POST /api/v1/sessions`). Store only a salted HMAC-SHA256 hash (`token_hash`) in the database.
- **Consequences:** Eliminates password vulnerabilities and PII liabilities. Requires clients to transmit credentials via Bearer header or cookie. Sessions expire after a configurable duration (default 24 hours).

---

## ADR-002: Deterministic Server-Side Educational Engine
- **Context:** Misconception diagnosis, scoring, and teach-back evaluation must follow strict pedagogical science and remain uniform across all interfaces.
- **Decision:** Implement all diagnosis rules (M1–M4, S1, U1), teach-back rubric evaluations (R1–R5), and concept mastery tracking authoritatively in Python (`src/learnloop/domain/`). Never duplicate or alter these rules in client-side TypeScript.
- **Consequences:** Guarantees diagnostic consistency, testability, and auditability. The frontend acts purely as a presentation layer for pedagogical feedback.

---

## ADR-003: ElevenLabs Voice Proxy with Bounded Timeout & Fallback
- **Context:** Synthesized tutor speech enhances student engagement, but external voice APIs can introduce latency, rate limits, or network failures.
- **Decision:** Proxy all voice requests through `POST /api/v1/voice/synthesize` on the backend. Never expose API keys to the browser. Enforce a strict 5.0-second timeout. If credentials are missing, quota is exhausted, or the request times out, return a structured fallback response and display tutor text.
- **Consequences:** The learning flow is completely resilient to voice provider downtime. All operational events are logged to `voice_events` for telemetry.

---

## ADR-004: Dual-Route Parallelism for Streamlit Demo Preservation
- **Context:** An independent Streamlit demonstration app (`app.py`) exists in the repository and must remain fully runnable as an independent demo backup.
- **Decision:** Mount `/api/v1` routes in parallel with legacy `/api` routes in `src/learnloop/api/main.py`. Retain legacy database models in `src/learnloop/db/models.py` alongside the normalized 15-entity relational schema.
- **Consequences:** Prevents regressions in `app.py` while establishing a clean, versioned, RESTful architecture for the React frontend and production services.

---

## ADR-005: Relational Normalization (15 Entities)
- **Context:** The application requires fine-grained tracking of sessions, lessons, concepts, questions, options, attempts, answers, explanations, tutoring dialogue, and hypotheses.
- **Decision:** Implement the 15 relational entities specified in `context.md` Section 16 using SQLAlchemy 2 declarative models supporting both SQLite (local verification) and PostgreSQL (production deployment).
- **Consequences:** Clean separation of concerns, strong foreign key constraints, atomic transaction boundaries, and auditability of learner progress over time.

