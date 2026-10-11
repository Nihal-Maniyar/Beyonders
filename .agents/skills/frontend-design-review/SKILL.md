---
name: frontend-design-review
description: >-
  Use this skill when implementing, refactoring, or reviewing the React 18 frontend, fraction
  visualizers (FractionBar, FractionCompare, FractionExplorer), learning studio UI views,
  audio controls, or accessibility (a11y) compliance.
---

# Frontend Design and Implementation Workflow for LearnLoop AI

This skill guides the implementation, visual review, and accessibility auditing of the React 18 + TypeScript + Vite frontend.

## Learning Studio Architectural Standards

1. **6 Core Views:**
   - `WelcomeView`: Low-friction session start without accounts.
   - `PreAssessmentView`: Clear question presentation, selection, and submission.
   - `LessonView`: Multi-part lesson explanations with worked examples.
   - `TutorView`: Reasoning input, empathetic misconception explanation, and audio playback.
   - `PracticeView`: Targeted practice and teach-back explanation entry.
   - `ProgressReportView`: Pre/post score comparison, percentage point delta, and concept mastery badges.

2. **Fraction Visualizer Design Rules:**
   - `FractionBar`: Renders proportional segments based on numerator and denominator. Must visibly demonstrate that larger denominators create smaller individual pieces.
   - `FractionCompare`: Side-by-side fraction strips for direct comparison (e.g., 2/3 vs 2/5).
   - `FractionExplorer`: Interactive slice toggle enabling students to build equal fractions visually.

## Step-by-Step Procedures

### 1. Component State Management & API Integration
- Keep component state clean:
  - Local state for active selections and input drafts.
  - Session hook (`useSession`) managing current session ID, token, and stage transition.
- Centralize API calls in `src/services/api-client.ts` with typed error handling:
  ```typescript
  export interface ApiError {
    code: string;
    message: string;
    details?: string[];
  }
  ```

### 2. Audio Player & Voice Fallback Handling
- Implement `VoiceControls` component:
  - Play button with audio waveform/speaker icon.
  - State machine: `idle` | `loading` | `playing` | `error`.
  - When backend returns voice failure or timeout:
    - Display non-blocking banner: *"Audio currently unavailable; text displayed below."*
    - Ensure tutor explanation text is rendered clearly in all cases.

### 3. Accessibility (a11y) Review Checklist
- Verify contrast ratios (minimum 4.5:1 for body text, 3:1 for large headings and buttons).
- Check keyboard navigation: every interactive element must be reachable via `Tab` and activatable via `Enter` / `Space`.
- Verify ARIA labels on custom SVG fraction bars (e.g., `aria-label="Fraction bar divided into 4 parts with 3 parts shaded"`).
- Run typecheck and production build:
  ```bash
  cd frontend && npm run build
  ```

