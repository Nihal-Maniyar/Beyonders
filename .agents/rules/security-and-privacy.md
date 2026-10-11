# Security and Privacy Rules

## 1. Anonymous Session Security
- No user accounts, registration, login forms, or persistent learner profiles.
- On session creation (`POST /api/v1/sessions`):
  - Generate a 32-byte cryptographic random token: `token = secrets.token_urlsafe(32)`.
  - Hash the token with HMAC-SHA256 using `SESSION_TOKEN_PEPPER`.
  - Store only the hash in `learning_sessions.token_hash`.
  - Return the public session `id` in the JSON response; deliver the secret token via an HttpOnly cookie or secure bearer authorization header.
- The public session `id` is NOT an authorization credential.
- Every private endpoint must validate token hash match, active status, and non-expiration.

## 2. Authorization and Resource Ownership
- Multi-tenant isolation: A session must never read, update, or submit answers for an attempt or reasoning response owned by another session.
- Query filters must strictly enforce `session_id == current_session.id`.

## 3. Secret Isolation
- `ELEVENLABS_API_KEY` and `SESSION_TOKEN_PEPPER` must strictly reside on the backend.
- Never prefix provider API keys with `VITE_` or expose them in client environment files.
- Never log provider keys, session tokens, or raw student audio in server logs.

## 4. Assessment Content Security
- Assessment endpoints (`GET /api/v1/assessments/{code}`) must strip all `is_correct` flags, answer keys, and scoring rubrics before returning data to the client.
- Correctness and points are computed strictly server-side on submission.
- Client-provided correctness, scores, or mastery levels must be rejected.

## 5. Untrusted Input Handling
- Treat all student reasoning text and message inputs as untrusted content.
- Sanitize inputs against injection attacks before storing or rendering.
- Tutor text must be escaped as text, never rendered as unescaped HTML (`dangerouslySetInnerHTML`).

