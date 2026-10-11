# LearnLoop AI — System Architecture Specification

> **Version:** 1.0.0  
> **Source of Truth:** [`context.md`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/context.md)  
> **System Scope:** Adaptive Fractions Learning Studio with Deterministic Misconception Diagnosis and Voice Support

---

## 1. Architectural Overview

LearnLoop AI is an educational technology system designed to teach foundational fraction concepts to young learners while deterministically detecting and remediating common mathematical misconceptions.

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING STUDIO (React 18)               │
│   • Welcome & Session Setup    • Pre-Assessment Benchmark   │
│   • Concept Lessons (C1-C3)    • Socratic Practice Studio   │
│   • Teach-Back Studio (R1-R5)  • Progress & Growth Report   │
│   • Fraction Visualizers (FractionBar, FractionCompare)     │
│   • Accessible VoicePlayer with Fallback Banner             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / REST (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND RUNTIME (/api/v1)              │
│   • Anonymous Session Auth Dependency (HMAC-SHA256)         │
│   • Standard Error Envelope Handler                         │
│   • Confidential Question Delivery (No answer leakage)      │
│   • Voice Proxy Controller (Bounded 5.0s Timeout)           │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│   DETERMINISTIC DOMAIN       │ │   ELEVENLABS VOICE PROXY   │
│   • Diagnosis Rules (M1-M4)  │ │   • Max 5s HTTP Timeout    │
│   • Teach-Back Rubric (R1-R5)│ │   • Graceful Text Fallback │
│   • Mastery Rules (4-item)   │ │   • Operational Telemetry  │
└──────────────┬───────────────┘ └─────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 RELATIONAL PERSISTENCE LAYER                │
│   • 15 Entities (SQLAlchemy 2 / SQLite & PostgreSQL)        │
│   • Learning Sessions, Concepts, Lessons, Questions         │
│   • Attempts, Answers, Reasoning Responses                  │
│   • Tutoring Interactions, Misconceptions, Voice Events     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystems & Responsibilities

### 2.1 React 18 Learning Studio Frontend
- **Framework:** React 18 functional components with strict TypeScript (`noImplicitAny: true`).
- **Styling:** Calm, distraction-free "learning studio" palette using semantic CSS design tokens.
- **Visualizers:** Interactive SVGs (`FractionBar`, `FractionCompare`, `FractionExplorer`) rendering unit fair-shares and proportions.
- **Audio Control:** [`VoicePlayer`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/frontend/src/components/common/VoicePlayer.tsx) rendering accessible playback controls and transparent fallback notices when voice is offline or unconfigured.

### 2.2 FastAPI API Runtime (`/api/v1`)
- **Anonymous Sessions:** Zero student logins or passwords. High-entropy secret token generated on creation; hashed with HMAC-SHA256 (`token_hash`) before database storage.
- **Session Scoping:** Every private endpoint authenticates via Bearer header or cookie and verifies resource ownership.
- **Confidential Delivery:** Question prompts and options never include `is_correct`, explanations, or answer keys.

### 2.3 Deterministic Educational Engine (Python Authority)
- **Misconception Diagnosis:**
  - `M1`: Whole-number bias (e.g., thinking 2/5 > 2/3 because 5 > 3).
  - `M2`: Reversed denominator rule (inverting inverse relationship).
  - `M3`: Numerator-only comparison (comparing top numbers while ignoring denominators).
  - `M4`: Invalid additive transformation for equivalent fractions.
  - `S1`: Arithmetic or transcription slip.
  - `U1`: Ambiguous or insufficient reasoning evidence (prompts Socratic clarifying question).
  - `NONE`: Correct option with sound reasoning.
- **Teach-Back Rubric Evaluation (R1–R5):**
  - Multi-criteria rubric evaluating student conceptual explanations.
- **Mastery Policy:** Requires 4 valid attempts across 3 distinct questions, $\ge 80\%$ accuracy, and passing a transfer question with valid reasoning.

### 2.4 ElevenLabs Voice Integration
- **Server-Side Proxy:** The browser never accesses ElevenLabs API keys or endpoints directly.
- **Bounded Timeout:** Outbound text-to-speech HTTP requests enforce a strict maximum 5.0-second timeout.
- **Graceful Fallback:** Voice failure, quota exhaustion, or unconfigured keys seamlessly return tutor text with a status notice.
- **Operational Auditing:** Every synthesis attempt is logged in `voice_events` with status, latency (`duration_ms`), and sanitized error codes.

---

## 3. Database Schema Architecture

The relational schema implements the 15 entities specified in `context.md` Section 16:
1. `learning_sessions`: Anonymous session identity, token hash, lifecycle.
2. `concepts`: Fraction concepts (C1, C2, C3).
3. `lessons`: Curriculum lessons and publication statuses.
4. `lesson_concepts`: Lesson-concept junction table.
5. `questions`: Question prompts and types.
6. `question_options`: Answer choices and internal correctness keys.
7. `question_concepts`: Question-concept junction table.
8. `assessments`: Assessment identity, types (pre, post, practice), versions.
9. `assessment_questions`: Ordered question membership and points possible.
10. `assessment_attempts`: Per-session assessment attempts.
11. `answer_submissions`: Question submissions per attempt.
12. `reasoning_responses`: Explanations linked to answer submissions.
13. `tutoring_interactions`: Ordered Socratic dialogue history.
14. `misconception_hypotheses`: Tentative misconception tracking and status.
15. `voice_events`: ElevenLabs telemetry and audit records.

---

## 4. Preservation of Streamlit Demo Backup

The independent Streamlit application ([`app.py`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/app.py)) is preserved with zero breaking changes:
- Legacy API endpoints (`/api/...`) remain mounted in [`src/learnloop/api/main.py`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/src/learnloop/api/main.py).
- Legacy database models (`LearnerModel`, `SessionModel`, `AttemptModel`, `ResponseModel`) coexist in [`src/learnloop/db/models.py`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/src/learnloop/db/models.py).

