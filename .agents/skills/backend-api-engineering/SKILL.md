---
name: backend-api-engineering
description: >-
  Use this skill when implementing, extending, or debugging LearnLoop AI FastAPI /api/v1 endpoints,
  session authorization dependencies, service coordinators, or ElevenLabs voice integration.
---

# Backend & API Engineering Workflow for LearnLoop AI

This skill guides implementation and maintenance of the FastAPI backend, anonymous session security, educational domain coordination, and server-side ElevenLabs voice integration.

## Core Responsibilities

1. **Versioned REST API (`/api/v1`):** Maintain strictly typed routes in `src/learnloop/api/v1/`.
2. **Anonymous Session Authentication:** Enforce session token validation via FastAPI dependencies (`src/learnloop/api/deps.py`).
3. **Educational Domain Integration:** Coordinate scoring and misconception diagnosis through `src/learnloop/domain/` without duplicating logic.
4. **ElevenLabs Voice Adapter:** Handle server-side audio synthesis with bounded timeouts and graceful text fallback.

## Step-by-Step Procedures

### 1. Implementing Session Authentication Dependency
```python
# src/learnloop/api/deps.py
async def get_current_session(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> LearningSessionModel:
    # 1. Extract bearer token or cookie
    # 2. Compute HMAC-SHA256 hash using SESSION_TOKEN_PEPPER
    # 3. Query learning_sessions where token_hash == computed_hash
    # 4. Check status == 'active' and expires_at > utc_now()
    # 5. Raise HTTPException(401) on failure
    ...
```

### 2. Assessment Endpoint Security
- When handling `GET /api/v1/assessments/{code}`:
  - Return questions ordered by position.
  - Return options with keys (`A`, `B`, etc.) and text.
  - Strip `is_correct` and internal explanations.
- When handling `POST /api/v1/attempts/{id}/answers`:
  - Verify attempt is in `in_progress` status.
  - Verify question belongs to that assessment.
  - Compute correctness and points server-side.
  - Store answer idempotently.

### 3. ElevenLabs Voice Synthesis Integration
- In `src/learnloop/integrations/elevenlabs.py`:
  - Read `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID` from `settings`.
  - Use `httpx.AsyncClient` with a strict `timeout=5.0` seconds.
  - Target URL: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`.
  - Request body: `{"text": tutor_text, "model_id": model_id}`.
  - In case of network error, 4xx/5xx status, or missing key:
    - Log error event in `voice_events` table with `status='failed'`.
    - Return a clean error code (`VOICE_UNAVAILABLE`) or stream text fallback notice.
    - Never crash the parent tutoring request.

### 4. Verification Steps
Run FastAPI test client suite:
```bash
pytest tests/api/test_fastapi_endpoints.py -v
```

