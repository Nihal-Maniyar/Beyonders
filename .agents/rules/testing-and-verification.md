# Testing and Verification Rules

## 1. Evidence-Based Verification Standard
- Never claim that a feature works without executing verified tests and inspecting actual test outputs.
- Any modification to domain logic, schemas, or API routes must be accompanied by automated tests.

## 2. Test Structure and Coverage
- **Unit Tests (`tests/unit/`):**
  - Mathematical diagnosis rules (`test_diagnosis_rules.py`): verify accurate inference of M1, M2, M3, M4, S1, U1, and NONE.
  - Assessment calculation rules (`test_mastery_and_assessment.py`): verify scoring, percentage point change calculations, and mastery progression.
  - Teach-back rubric evaluations (`test_teachback_rules.py`): verify scoring across criteria R1–R5.
- **Integration Tests (`tests/integration/`):**
  - Session data isolation: verify Session A cannot query or mutate Session B data.
  - Transaction atomicity & rollback: verify failed operations leave the database in a clean state.
  - Database seed validation: verify initial seed populates concepts C1–C3, lessons, assessments, questions, and options.
- **API Tests (`tests/api/`):**
  - Session lifecycle: create, validate, expire.
  - Assessment attempts: start attempt, submit answer, complete attempt.
  - Voice endpoint: test successful synthesis, timeout handling, missing key graceful fallback.
- **Frontend Verification:**
  - `npm run build` must succeed without TypeScript errors.
  - End-to-end browser walkthrough verifying the complete 11-step learning loop.

## 3. Preservation of Existing Tests
- Existing tests represent verified educational logic. Never delete or weaken test assertions to force failing code to pass.

