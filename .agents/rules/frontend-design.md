# Frontend Design and UI/UX Rules

## 1. Route Map
Frontend routes must correspond to the logical learning stages:
- `/`: Welcome & start anonymous learning session.
- `/session/:id/assessment/pre`: Pre-assessment question flow.
- `/session/:id/lesson/:lessonId`: Fraction concept lessons with worked examples.
- `/session/:id/tutor`: Reasoning prompt, diagnostic feedback, and spoken tutor interaction.
- `/session/:id/practice`: Targeted remediation activities and teach-back input.
- `/session/:id/assessment/post`: Post-assessment verification.
- `/session/:id/progress`: Detailed progress report and concept outcomes.

## 2. Visual Style & Layout
- Warm, calm editorial learning studio: cream background (`#FDFBF7`), soft stone borders (`#E5E0D8`), slate text (`#1E293B`), terracotta accents (`#C25E3E`), and forest green highlights (`#2D6A4F`).
- Responsive layout supporting desktop and tablet viewports.
- Clear Stage Stepper showing progress across the 6 learning steps.

## 3. Mathematical Fraction Visualizers
- Components (`FractionBar`, `FractionCompare`, `FractionExplorer`):
  - Must accurately render proportional widths corresponding to denominators and numerators.
  - Fractions with larger denominators must visually render smaller individual parts.
  - Interactive slice toggling must visually reflect fraction values.
  - Never render purely decorative or misleading geometric shapes.

## 4. Voice Controls & Fallback UI
- Audio playback controls:
  - Visible button to trigger or replay tutor audio.
  - Visual loading spinner while voice synthesis is in progress.
  - Clear, accessible playback status indicator.
  - In case of voice failure or timeout, show an inline non-blocking notice: *"Spoken audio unavailable; displaying tutor text below."*
  - Tutor text must always remain visible and accessible regardless of voice state.

## 5. Accessibility (a11y)
- Semantic HTML tags (`<nav>`, `<main>`, `<article>`, `<button>`).
- Keyboard focus outlines on all interactive elements.
- Accessible ARIA labels on fraction SVG bars (e.g., `aria-label="Fraction bar showing 3 fourths shaded"`).

