# API Conventions Rules

## 1. Route Paths and Versioning
- All public REST API endpoints must be mounted under `/api/v1/`.
- Required core endpoint inventory:
  - `POST /api/v1/sessions`: Create anonymous session.
  - `GET /api/v1/sessions/current`: Fetch current session lifecycle status.
  - `DELETE /api/v1/sessions/current`: End or expire session.
  - `GET /api/v1/lessons`: List published fraction lessons.
  - `GET /api/v1/lessons/{lesson_id}`: Fetch detailed lesson content with visualizer metadata.
  - `GET /api/v1/assessments/{code}`: Fetch safe assessment definition (questions and options, with answer keys stripped).
  - `POST /api/v1/assessments/{code}/attempts`: Start a new attempt.
  - `GET /api/v1/attempts/{attempt_id}`: Fetch attempt progress and status.
  - `POST /api/v1/attempts/{attempt_id}/answers`: Submit answer for a question in an active attempt.
  - `POST /api/v1/answers/{answer_id}/reasoning`: Submit reasoning explanation for a submitted answer.
  - `POST /api/v1/tutor/messages`: Send learner message to adaptive tutor.
  - `POST /api/v1/tutor/teach-back`: Submit free-text teach-back explanation for rubric evaluation.
  - `POST /api/v1/attempts/{attempt_id}/complete`: Finalize attempt and calculate final score atomically.
  - `GET /api/v1/progress`: Retrieve derived progress summary, pre/post comparison, and misconception history.
  - `POST /api/v1/voice/synthesize`: Server-side ElevenLabs voice synthesis endpoint.
  - `GET /api/v1/health`: Sanitized health check.

## 2. Standard Error Format
All errors must return the standard envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The selected option is invalid for this question.",
    "details": []
  }
}
```

## 3. Session Authentication & Isolation
- Private endpoints must depend on `deps.get_current_session`.
- Missing token -> HTTP 401 Unauthorized.
- Expired session -> HTTP 401 Unauthorized.
- Accessing attempts or answers created by a different session -> HTTP 403 Forbidden or HTTP 404 Not Found.
- No sensitive internals (stack traces, SQL statements, provider API keys) may be returned in error bodies.

