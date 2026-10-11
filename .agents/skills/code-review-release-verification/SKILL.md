---
name: code-review-release-verification
description: >-
  Use this skill when conducting pre-release verification, checking Definition of Done and acceptance
  criteria against context.md Section 35, auditing Streamlit backup health, and checking documentation synchronization.
---

# Code Review & Release Verification Workflow for LearnLoop AI

This skill provides the final gatekeeping workflow before completing milestones or presenting the live hackathon demonstration.

## Gate 1: Acceptance Criteria Checklist (`context.md` Section 35)

Verify that every condition is met with concrete evidence:
- [ ] Anonymous session starts without registration.
- [ ] Unique anonymous session is created and validated via token hash.
- [ ] Session data cannot be accessed by another session.
- [ ] Fraction pre-assessment is delivered (without answer keys) and scored on server.
- [ ] Fraction teaching content is displayed with accurate visual representations.
- [ ] Tutor asks for reasoning and records response linked to submitted answer.
- [ ] Feedback correctly identifies tentative misconception (M1–M4).
- [ ] At least one targeted follow-up practice question is completed.
- [ ] Post-assessment records a distinct second attempt.
- [ ] Progress report computes percentage-point change without fabricating results.
- [ ] ElevenLabs spoken tutor output operates successfully in the live demo.
- [ ] Text tutoring remains completely usable if voice fails or times out.
- [ ] No provider credentials or secrets exposed to browser bundles or Git.
- [ ] Streamlit application (`app.py`) runs independently without errors.
- [ ] Documentation (`docs/`) matches actual implementation.

## Gate 2: Streamlit Backup Smoke Test

Execute the Streamlit application in headless mode to guarantee live-demo contingency:
```bash
streamlit run app.py --server.headless=true
```
Confirm:
1. Streamlit initializes without import errors.
2. Content bank loads successfully.
3. Database engine connects cleanly.

## Gate 3: Definition of Done Audit

Before marking any phase complete:
1. Code implements the approved requirement.
2. Existing useful behavior is preserved.
3. Relevant unit and integration tests run and pass.
4. Error, empty, and loading states are handled.
5. No uncommitted secrets exist.
6. Documentation files (`docs/architecture.md`, `docs/api.md`, `docs/database.md`, `docs/er-diagram.mmd`) reflect current code.
7. Verification results are reported factually without exaggeration.

