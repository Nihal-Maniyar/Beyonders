# Architecture and Project Structure Rules

## 1. Single Source of Truth
- `context.md` (v1.0) is the approved specification and master contract.
- The Python educational domain engine (`src/learnloop/domain/`) is the sole authoritative implementation of educational rules:
  - Misconception diagnosis (`diagnosis_rules.py`)
  - Scoring & pre/post comparison (`assessment_rules.py`)
  - Mastery criteria progression (`mastery_rules.py`)
  - Teach-back rubric evaluation (`teachback_rules.py`)
- Client-side code in TypeScript must never duplicate or re-implement scoring calculations or misconception detection algorithms.

## 2. Layering and Separation of Concerns
- **API Layer (`src/learnloop/api/v1/`):** Responsible only for HTTP protocol handling, input schema parsing (Pydantic), calling service layer methods, status codes, and error envelopes. No complex educational or scoring logic in routes.
- **Service Layer (`src/learnloop/services/`):** Coordinates business workflows (session lifecycle, assessment attempt progression, reasoning submission, voice synthesis coordination).
- **Domain Layer (`src/learnloop/domain/`):** Pure deterministic educational functions, mathematical validations, rubric scoring.
- **Persistence Layer (`src/learnloop/db/`):** SQLAlchemy 2 declarative models and scoped session management.
- **Integrations Layer (`src/learnloop/integrations/`):** External provider adapters (ElevenLabs client). Must encapsulate provider-specific HTTP headers, payloads, and timeout handling.

## 3. Preserved Artifacts
- `app.py` must remain directly runnable with `streamlit run app.py`. Any shared dependencies or database utilities must maintain backward compatibility with the Streamlit entry point.
- Avoid introducing unnecessary third-party infrastructure (e.g., Redis, Celery, Docker Swarm, external auth services).

