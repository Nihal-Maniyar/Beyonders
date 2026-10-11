---
name: automated-testing
description: >-
  Use this skill when writing, executing, or debugging LearnLoop AI unit tests,
  FastAPI TestClient integration tests, session isolation tests, or full end-to-end learning loop verification.
---

# Automated Testing Workflow for LearnLoop AI

This skill provides testing procedures across unit, integration, API, and end-to-end scopes to guarantee educational logic correctness and data integrity.

## Test Pyramid

1. **Unit Tests (`tests/unit/`):**
   - Misconception diagnosis rules (`test_diagnosis_rules.py`): verify accurate detection of M1, M2, M3, M4, S1, U1.
   - Assessment scoring (`test_mastery_and_assessment.py`): verify raw score, maximum score, percentage point calculation.
   - Teach-back rubric evaluation (`test_teachback_rules.py`): verify criteria R1–R5 point allocations.
2. **Integration Tests (`tests/integration/`):**
   - Multi-tenant persistence isolation (`test_persistence_isolation.py`): verify Session A cannot see Session B's attempts.
   - Transaction rollback safety: verify simulated mid-attempt exceptions leave database uncorrupted.
3. **API Tests (`tests/api/`):**
   - Route validation using `fastapi.testclient.TestClient`.
   - Verify question endpoints do not expose `is_correct`.
   - Verify ElevenLabs mock synthesis and timeout handling.

## Step-by-Step Procedures

### 1. Running Unit and Integration Tests
Execute the full test suite with detailed output:
```bash
pytest -v --strict-markers
```

Run specific test modules:
```bash
# Educational domain rules
pytest tests/unit/test_diagnosis_rules.py -v
pytest tests/unit/test_mastery_and_assessment.py -v
pytest tests/unit/test_teachback_rules.py -v

# API endpoints
pytest tests/api/test_fastapi_endpoints.py -v

# Persistence and session isolation
pytest tests/integration/test_persistence_isolation.py -v
```

### 2. ElevenLabs Integration Mock Testing
Ensure voice endpoint tests mock the HTTP client to simulate:
1. Normal audio synthesis (200 OK with audio/mpeg).
2. Provider timeout (> 5.0 seconds -> 504 / safe fallback).
3. Missing API key (503 / graceful fallback).

### 3. Frontend Typecheck and Build Verification
Ensure the frontend builds with zero errors:
```bash
cd frontend && npm run build
```

### 4. End-to-End Learning Loop Rehearsal
Verify the 11-step journey specified in `context.md` Section 29:
1. Create session -> 2. Pre-assessment -> 3. Fraction lesson -> 4. Mistake -> 5. Reasoning -> 6. Misconception feedback -> 7. Targeted practice -> 8. Post-assessment -> 9. Progress report -> 10. Spoken voice interaction -> 11. Text fallback confirmation.

