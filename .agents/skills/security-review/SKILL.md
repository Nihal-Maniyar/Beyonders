---
name: security-review
description: >-
  Use this skill when auditing LearnLoop AI for anonymous session isolation, token hash verification,
  secret containment, assessment answer key leakage prevention, or input sanitization.
---

# Security Review Workflow for LearnLoop AI

This skill provides an automated and manual security inspection checklist to prevent privacy leaks, unauthorized cross-session access, and secret exposure.

## Security Boundaries & Critical Checkpoints

### 1. Anonymous Session Token Security
- **Checkpoint:** Verify session token generation uses `secrets.token_urlsafe(32)`.
- **Checkpoint:** Verify that only the HMAC-SHA256 hash (`token_hash`) is stored in the database.
- **Checkpoint:** Verify public session ID (`id`) is never accepted as an authorization bearer.
- **Verification Command:**
  ```python
  # Check that token hashing is one-way and salted/peppered
  python -c "import hashlib, hmac; h = hmac.new(b'pepper', b'token123', hashlib.sha256).hexdigest(); print(len(h))"
  ```

### 2. Multi-Tenant Session Isolation
- **Checkpoint:** Verify that all database queries for attempts, answers, and tutoring interactions filter by `session_id == current_session.id`.
- **Checkpoint:** Execute test `test_multi_learner_data_isolation` to prove that Session A receives HTTP 403 or HTTP 404 when requesting Session B's attempt ID.

### 3. Assessment Content Leakage Audit
- **Checkpoint:** Inspect `GET /api/v1/assessments/{code}` response schema.
- **Checkpoint:** Confirm that `is_correct`, `points_awarded`, and private question explanations are strictly omitted from public question and option objects.
- **Checkpoint:** Confirm that correct answers are never sent in browser data attributes or hidden input fields.

### 4. Secret & Credential Containment
- **Checkpoint:** Confirm that `.env` is listed in `.gitignore`.
- **Checkpoint:** Confirm that `frontend/` source code contains ZERO occurrences of `ELEVENLABS_API_KEY` or `SESSION_TOKEN_PEPPER`.
- **Checkpoint:** Confirm that frontend `vite.config.ts` does NOT expose server secrets through `define` or `VITE_` prefixes.

### 5. Input Sanitization & Tutor Prompt Safety
- **Checkpoint:** Ensure student reasoning text inputs are validated for maximum length (e.g., 2000 characters).
- **Checkpoint:** Verify tutor output is rendered as plain text or properly sanitized markdown, never unescaped HTML.

