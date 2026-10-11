# LEARNLOOP AI — MASTER PROJECT CONTEXT & IMPLEMENTATION SPECIFICATION

**Project:** LearnLoop AI — Adaptive AI Tutor & Misconception Detector  
**Hackathon:** VORTEXA 3.0  
**Domain:** AI-Powered Education & Learning Technology  
**Problem Statement:** E-01  
**Primary objective:** Build an evidence-driven AI tutor that identifies why a student misunderstands a concept, adapts its teaching, evaluates the student's understanding, and tracks learning progress.

---

# 1. INSTRUCTIONS TO THE AI RECEIVING THIS DOCUMENT

You are joining an existing hackathon project as a technical architect, coding assistant, debugger, and implementation partner.

Read this entire document before proposing architecture, generating code, changing files, or adding features.

Your job is to help the team finish a working, demonstrable implementation within its remaining hackathon time.

Follow these rules:

1. Prioritise a complete working learning loop over additional features.
2. Do not redesign the project unnecessarily.
3. Do not introduce technologies or dependencies without a clear reason.
4. Do not assume that a feature is implemented simply because it is described here.
5. Inspect the existing codebase before creating, replacing, or reorganising files.
6. Preserve working code and integrate with the existing implementation.
7. Use simple, modular code appropriate for a beginner team.
8. Prefer verified, deterministic educational logic over unrestricted LLM-generated answers.
9. Never fabricate student attempts, assessment results, mastery scores, or successful API responses.
10. Do not spend the remaining time implementing features explicitly marked as future additions.
11. Test the entire learning flow after every significant integration.
12. Explain where files belong, how to run the application, required environment variables, and how to test each feature.
13. If information is missing, distinguish confirmed requirements from assumptions. Ask only when the missing information blocks implementation.
14. Never claim that a feature works until it has been implemented and tested.
15. Keep the project aligned with the supplied VORTEXA 3.0 rules, including any requirements for original implementation, AI-tool disclosure, and permitted AI assistance.

**Immediate task:** Inspect the existing project, identify what is already functional, compare it against the required MVP below, and implement the highest-priority missing functionality.

---

# 2. PROJECT VISION

LearnLoop AI is an adaptive educational tutor that helps students learn a topic, identify misunderstandings, explain what they have learned, and receive personalised corrective feedback.

The system must not behave like a generic chatbot that simply answers questions.

Instead, it follows a structured learning process:

1. The teacher provides or approves the syllabus.
2. The AI organises the syllabus into concepts and learning objectives.
3. The student completes a pre-assessment before teaching begins.
4. The system examines answers and reasoning to identify possible misconceptions.
5. The AI teaches concepts according to the student's demonstrated needs.
6. The student answers practice questions and receives adaptive follow-up questions.
7. The student explains the topic back to the AI in their own words.
8. The system evaluates the explanation against an explicit concept rubric.
9. The tutor identifies missing or misunderstood concepts and teaches them again.
10. A post-assessment measures the change in performance.
11. The system records evidence and updates concept-level mastery.
12. Future revision quizzes are scheduled according to demonstrated learning needs.

Voice interaction makes this experience more natural and accessible.

The defining product principle is:

**LearnLoop AI does not merely tell students whether an answer is right or wrong. It investigates their reasoning, tests its interpretation, and adapts the next learning activity based on evidence.**

The tutor supports teachers; it does not replace them.

---

# 3. PROBLEM STATEMENT REQUIREMENTS

The implementation must address every core requirement of E-01.

## R1. Teach one topic accurately

The tutor must explain concepts using examples, analogies, worked examples, and step-by-step reasoning.

Generated explanations must remain faithful to verified learning material.

## R2. Diagnose incorrect answers

The system must examine the student's answer and reasoning to identify a likely misconception.

It must distinguish a conceptual misunderstanding from an ordinary arithmetic slip where the available evidence permits.

If the evidence is insufficient, the tutor must ask a clarifying question rather than invent a diagnosis.

## R3. Personalise feedback

Two students who give different incorrect answers to the same question must receive different diagnoses and different follow-up activities when their reasoning supports those distinctions.

## R4. Track demonstrated mastery

The system must maintain a record of learner performance for each concept.

Mastery must be calculated from recorded work, not from a student's claim that they understand a topic.

## R5. Compare pre-assessment and post-assessment

The application must support a repeatable pre/post assessment using the same items.

It must calculate the observed score change and disclose the sample size and relevant limitations.

## R6. Maintain teacher oversight

The tutor must be presented as a learning aid, not a replacement for teachers. Teacher-provided content and oversight should be supported.

---

# 4. TARGET USERS AND THEIR RESPONSIBILITIES

## 4.1 Teacher

The teacher provides or approves:

- Subject and chapter.
- Syllabus or learning material.
- Learning objectives.
- Concepts that must be covered.
- Important prerequisites, if known.
- Approved explanations and reference material.

The teacher remains responsible for approving the syllabus and checking educational content.

For the MVP, teacher input can be a simple text field containing a chapter outline. A full teacher account and content-management system are unnecessary.

## 4.2 Student

The student can:

- Select a prepared chapter.
- Complete a pre-assessment.
- Learn a concept.
- Answer quizzes.
- Explain their reasoning.
- Ask for clarification.
- Listen to the tutor's response.
- Speak rather than type when voice input is available.
- Explain the topic back to the AI.
- Review mistakes.
- View progress and upcoming revision tasks.

## 4.3 AI tutor

The AI tutor must:

- Follow the approved syllabus.
- Use verified material for educational explanations.
- Evaluate responses against defined criteria.
- Identify possible misconceptions with supporting evidence.
- Ask clarifying questions when necessary.
- Select appropriate follow-up activities.
- Evaluate student explanations using a rubric.
- Update learner records only from actual interactions.
- Communicate uncertainty honestly.

---

# 5. IMPLEMENTATION STRATEGY: FINISH THE MVP FIRST

The complete vision is larger than the amount of time available in a short hackathon.

Build the smallest version that satisfies the problem statement end to end.

## P0 — Mandatory core implementation

These features must take priority over everything else.

1. One working subject and chapter: comparing fractions.
2. A prepared, verified syllabus divided into concepts.
3. A pre-assessment.
4. An answer-checking and misconception-detection engine.
5. Clarifying questions for ambiguous reasoning.
6. Adaptive teaching and targeted follow-up questions.
7. Student teach-back, using text at minimum.
8. Rubric-based evaluation of the student's explanation.
9. Identification of missing or misunderstood concepts.
10. A targeted remedial activity.
11. Persistent learner-attempt records.
12. Evidence-based concept mastery.
13. Repeatable pre/post assessment with a calculated report.
14. A functional user interface and a reliable demonstration.

## P1 — Voice features

Implement after P0 is working.

1. Text-to-speech for tutor explanations and feedback.
2. Speech-to-text for student answers.
3. Automatic microphone activation when the student enters teach-back mode, subject to browser permissions and technical support.
4. A visible recording state, stop control, and transcript correction.
5. A text-only fallback if voice services fail.

## P2 — Lightweight personalisation

Implement only if time remains after P0 and P1.

1. Persist a next-review date for each concept.
2. Display quizzes that are due.
3. Generate a revision quiz from recorded misconceptions.
4. Show a basic learner progress dashboard.

## Future additions — DO NOT BUILD IN THIS HACKATHON

These are part of the long-term product vision, not current implementation requirements:

- Multi-subject and multi-grade support.
- Automatic import and parsing of arbitrary PDFs and textbooks.
- A complete teacher portal with accounts, classes and permissions.
- Multi-student classroom analytics.
- Push notifications, email reminders and background scheduling infrastructure.
- Advanced spaced-repetition algorithms.
- Long-term retention experiments.
- Full autonomous, real-time voice conversations with interruption handling.
- Custom-trained educational AI models.
- Advanced knowledge graphs and prerequisite inference.
- LMS integrations.
- Mobile applications.
- Student leaderboards and gamification.
- Parental dashboards.
- Production-scale deployment and monitoring.
- Fine-tuning models on student interactions.

Do not implement these features merely because they appear in the vision.

---

# 6. INITIAL SUBJECT AND VERIFIED CONTENT

The MVP must focus on comparing fractions.

This topic is deliberately narrow: it is easy to demonstrate, allows meaningful misconception diagnosis, and can be validated mathematically.

## 6.1 Concept structure

### C1 — Understanding fractions

Learning objectives:

- Identify the numerator.
- Identify the denominator.
- Understand equal-sized parts of a whole.
- Interpret a fraction as a quantity.

### C2 — Comparing fractions

Learning objectives:

- Compare fractions with equal numerators.
- Compare fractions with equal denominators.
- Compare fractions using equivalent fractions or a common denominator.
- Understand why a larger denominator does not automatically mean a larger fraction.

### C3 — Equivalent fractions

Learning objectives:

- Understand why equivalent fractions have the same value.
- Multiply or divide numerator and denominator by the same nonzero factor.
- Recognise invalid transformations.

The teacher can provide another chapter in the future, but the initial demo should use this prepared content.

## 6.2 Verified example

Question: Which is larger, 2/5 or 2/3?

Correct answer: 2/3.

Explanation: If the whole is the same size, dividing it into three equal parts produces larger individual parts than dividing it into five equal parts. Therefore, two-thirds is greater than two-fifths.

Do not assume that every wrong answer to this question has the same cause.

## 6.3 Content representation

Store the content in a structured format such as JSON.

Each concept should contain:

- `concept_id`
- `title`
- `learning_objectives`
- `prerequisites`
- `verified_explanation`
- `worked_examples`
- `source_reference`
- `question_ids`
- `rubric_items`
- `misconception_ids`

Each question should contain:

- `question_id`
- `concept_id`
- `question_text`
- `question_type`
- `options`, where applicable
- `correct_answer`
- `verified_explanation`
- `difficulty`
- `misconception_mappings`
- `remediation_activity_ids`

Answer keys and essential mathematical facts must be defined and validated, not generated freely at runtime.

---

# 7. COMPLETE LEARNING WORKFLOW

## Stage 1 — Syllabus preparation

The teacher provides the chapter name, learning objectives, or a short syllabus.

The system organises it into a sequence of concepts.

For the MVP, a predefined fraction syllabus is sufficient.

If an LLM is used to help organise teacher input, its proposed outline must be checked against the approved material before teaching begins.

The application must show the concepts that will be covered.

## Stage 2 — Pre-assessment

Before teaching, present six fixed questions:

- Two questions for C1.
- Two questions for C2.
- Two questions for C3.

Store every submitted answer with its question ID, correctness, learner ID and assessment phase.

Do not reveal the full answer key before the post-assessment.

Use the recorded answers to identify areas that need attention.

The pre-assessment must be completed before the teaching phase, but diagnosis of an incorrect answer can be deferred to the teaching workflow if necessary.

## Stage 3 — Teach a concept

Teach one concept at a time.

Each lesson should include:

1. A simple definition.
2. An intuitive example.
3. A worked example.
4. A visual aid when helpful.
5. A short comprehension question.

The explanation must come from approved content.

An LLM may improve wording or provide conversational phrasing, but it must not invent unsupported facts or contradict the verified source.

## Stage 4 — Quiz and reasoning capture

After the lesson, present a question.

When the answer is incorrect, ask the learner why they selected it.

A structured answer plus a short explanation is ideal.

The tutor should distinguish:

- Correct answer with reasonable supporting evidence.
- Incorrect answer with a recognisable misconception.
- Incorrect answer caused by a likely calculation slip.
- Unclear or contradictory reasoning.
- Correct answer with reasoning that reveals a misunderstanding.

The system must not confuse correctness with understanding.

## Stage 5 — Misconception diagnosis

Use the misconception engine described in Section 8.

A diagnosis must include its evidence and a confidence or certainty category.

If the student provides insufficient reasoning, ask a clarifying question.

## Stage 6 — Targeted remediation

Choose a follow-up activity based on the diagnosis.

Examples:

- Whole-number bias → compare visual fraction strips.
- Incorrect denominator rule → compare equal-sized wholes divided into different numbers of parts.
- Invalid equivalent-fraction rule → show how numerator and denominator scale proportionally.
- Arithmetic slip → ask the learner to retry a similar calculation.
- Unclear reasoning → ask the learner to explain their method.

The system must record which activity was delivered and what happened afterward.

## Stage 7 — Student teach-back

After the chapter or selected concepts have been taught, prompt:

"Explain what you understood about this topic in your own words. You can use an example to help explain your thinking."

The student can type their response or use speech recognition.

For the MVP, text input is mandatory. Automatic speech input is an enhancement.

Evaluate the explanation against a predefined rubric.

The tutor must identify:

- Concepts demonstrated correctly.
- Concepts explained partially.
- Concepts missing from the explanation.
- Incorrect claims or misconceptions.
- Areas requiring clarification.

An omitted concept should initially be classified as "not demonstrated," not automatically as "misunderstood."

## Stage 8 — Teach-back feedback

Generate feedback from the rubric results.

For example:

"You explained that the denominator represents the number of equal parts, and you correctly understood that smaller equal parts result from dividing the same whole into more pieces. However, you have not yet demonstrated how to compare fractions with different numerators and denominators. Let's practise that next."

The feedback must reflect the student's actual response.

Do not produce a generic praise message or unsupported mastery percentage.

## Stage 9 — Targeted final quiz

Generate or select questions that test the missing concepts.

Prefer verified questions from the content bank.

If an LLM creates a new question, validate it against the learning objective and answer key before using it for scoring. If reliable validation is not possible, use a prepared question.

## Stage 10 — Post-assessment

Present the same six fixed questions used in the pre-assessment.

Calculate scores from saved answers.

Report:

- Pre-assessment score.
- Post-assessment score.
- Absolute change in percentage points.
- Number of learners with complete paired results.
- Concept-level performance, where available.
- Limitations of the evaluation.

Do not claim that improvement was caused by the tutor based solely on a pre/post comparison.

## Stage 11 — Mastery and review

Recalculate concept mastery from actual learner attempts.

Store the next-review date if the review feature has been implemented.

For the MVP, a simple review queue is sufficient. A production scheduler is not required.

---

# 8. MISCONCEPTION ENGINE SPECIFICATION

This engine is the central intellectual component of the application.

## 8.1 Initial misconception library

### M1 — Whole-number bias

Evidence: The learner says that 2/5 is larger than 2/3 because five is larger than three.

Interpretation: The learner compares denominator values as whole numbers instead of reasoning about the size of the parts.

Follow-up: Use two identical wholes divided into five and three equal parts.

### M2 — Reversed denominator rule

Evidence: The learner consistently claims that a larger denominator produces a larger fraction when numerators are equal.

Interpretation: The learner may have reversed the relationship between the number of equal parts and the size of each part.

Follow-up: Compare one piece from wholes divided into two and eight equal parts.

### M3 — Numerator-only comparison

Evidence: The learner decides which fraction is larger by comparing only the numerators, ignoring the denominators.

Interpretation: The learner is applying an incomplete comparison rule.

Follow-up: Compare fractions with different numerators and denominators and use a common denominator or visual model.

### M4 — Invalid equivalent-fraction transformation

Evidence: The learner claims that adding the same number to numerator and denominator always preserves the value of a fraction.

Interpretation: The learner does not understand that equivalent fractions require proportional scaling of numerator and denominator.

Follow-up: Compare 1/2 with 2/3 and show why adding one to both parts changes the value.

### S1 — Likely arithmetic slip

Evidence: The student's method is valid, but a calculation or transcription error produces the wrong answer.

Interpretation: There is not enough evidence of a conceptual misconception.

Follow-up: Ask the learner to retry a similar calculation.

### U1 — Insufficient evidence

Evidence: The answer is wrong, but the learner provides no useful reasoning or gives contradictory explanations.

Interpretation: The cause is unknown.

Follow-up: Ask a focused clarifying question before assigning a specific misconception.

These patterns are initial hypotheses, not a complete taxonomy of mathematical misconceptions.

## 8.2 Diagnosis output contract

The diagnostic engine should return a structured object similar to:

{
  "question_id": "Q_COMPARE_01",
  "correct": false,
  "diagnosis": "M1",
  "certainty": "high",
  "evidence": "The student explicitly compared 5 and 3 as whole numbers.",
  "clarification_required": false,
  "next_activity_id": "A_FRACTION_STRIPS"
}

This is a schema example, not a fixed result.

Allowed diagnosis values:

- `M1`
- `M2`
- `M3`
- `M4`
- `S1`
- `U1`
- `NONE`

Use an explicit, limited output schema for any LLM classification.

## 8.3 Classification procedure

1. Check the answer against the verified answer key.
2. Inspect the question, available reasoning and previous attempts.
3. Match the evidence to the misconception library.
4. Select a tentative diagnosis.
5. Record the evidence supporting it.
6. If the evidence is insufficient, choose U1 and ask a clarifying question.
7. Select the corresponding remediation activity.
8. Record the result.

Do not let the LLM choose an arbitrary misconception outside the approved list.

For structured multiple-choice questions, use deterministic answer mappings where possible.

For free-text reasoning, an LLM can classify the response into the approved categories.

If the LLM returns invalid JSON, an unknown diagnosis, contradictory evidence, or a result unrelated to the question, reject the result and fall back to U1 or a clarification request.

Do not treat the LLM's self-reported confidence as a calibrated probability.

## 8.4 Adaptive behaviour

The system must demonstrate that different reasoning produces different outcomes.

Example:

Student A: "2/5 is larger because five is larger than three."

Expected diagnosis: M1.

Expected activity: visual fraction-strip comparison.

Student B: "2/5 is larger because the fraction with the larger denominator is always larger."

Expected diagnosis: M2, provided the reasoning supports this distinction.

Expected activity: comparison of individual pieces of identical wholes.

If the two responses do not provide enough evidence to distinguish the misconceptions, the system should ask different clarifying questions or temporarily retain an uncertain diagnosis.

---

# 9. STUDENT TEACH-BACK EVALUATION

The teach-back is a major differentiator and must be implemented using a rubric rather than an unrestricted AI-generated percentage.

## 9.1 Example rubric for the fractions chapter

Required criteria:

1. Explains numerator and denominator correctly.
2. Understands that fraction parts must be equal-sized.
3. Understands how the number of equal parts affects part size.
4. Compares fractions using a valid method.
5. Explains equivalent fractions correctly.

Assign each criterion one of these statuses:

- `demonstrated`
- `partial`
- `incorrect`
- `not_demonstrated`

The evaluator should return a result similar to:

{
  "criterion_results": [
    {
      "criterion_id": "R1",
      "status": "demonstrated",
      "evidence": "The student correctly explained the denominator."
    },
    {
      "criterion_id": "R2",
      "status": "not_demonstrated",
      "evidence": "The explanation did not address equal-sized parts."
    }
  ],
  "overall_feedback": "The student demonstrated some core ideas but needs more practice comparing fractions.",
  "recommended_concepts": ["C2"]
}

The example is illustrative and does not represent an actual learner.

## 9.2 Scoring

For a simple MVP rubric, assign:

- Demonstrated = 1 point.
- Partial = 0.5 points.
- Incorrect = 0 points.
- Not demonstrated = 0 points.

Calculate:

`Rubric coverage = earned points / total possible points × 100`

Call the result "rubric coverage" or "explanation score."

It measures how well the student's explanation demonstrated the selected criteria. It is not a definitive measure of knowledge, intelligence, or long-term retention.

The system should explain which criteria were satisfied and which were not.

## 9.3 Reliability safeguards

- Provide the evaluator with the approved rubric.
- Ground evaluation in the student's actual response.
- Do not reward verbosity over correctness.
- Allow clarification when a response is ambiguous.
- Distinguish a missing explanation from an explicitly wrong claim.
- Do not treat a speech-recognition error as proof that the learner lacks knowledge.
- Use prepared follow-up questions when an evaluation is uncertain.

---

# 10. VOICE INTERACTION SPECIFICATION

Voice is an interaction layer, not a replacement for the educational engine.

## 10.1 Text-to-speech

Provide a "Listen" control next to tutor explanations and feedback.

The system should:

1. Use the same approved text shown on screen.
2. Convert that text into audio.
3. Play the audio.
4. Allow the learner to replay it.
5. Keep the text visible and accessible.

Use ElevenLabs if the team has access to the required API and credentials.

Do not make TTS mandatory for the app to function.

## 10.2 Speech-to-text

Provide a microphone option for answers and explanations.

When the student enters teach-back mode:

1. Request microphone permission if it has not already been granted.
2. Automatically begin listening where browser support allows.
3. Display a visible recording indicator.
4. Capture speech and obtain a transcript.
5. Let the student stop or correct the transcript.
6. Submit the transcript to the same learning engine used for typed answers.
7. Save the transcript or an appropriate text record alongside the attempt.

If automatic speech recognition is unavailable, show a clear manual recording or text-entry fallback.

## 10.3 Technical distinction

Text-to-speech and speech-to-text are separate capabilities.

ElevenLabs voice generation should not be assumed to provide transcription in every product configuration.

Before implementing voice, verify:

- Available API endpoints.
- API credentials.
- Supported input and output formats.
- Browser compatibility.
- Network access.
- Latency and rate limits.
- Whether the chosen service can transcribe speech.

Do not hardcode API keys or expose them in client-side code.

## 10.4 Natural conversation

The tutor should maintain a structured conversation state:

- `TEACHING`
- `ASKING_QUESTION`
- `AWAITING_RESPONSE`
- `DIAGNOSING`
- `CLARIFYING`
- `REMEDIATING`
- `TEACH_BACK`
- `EVALUATING`
- `ASSESSMENT`
- `COMPLETE`

Only introduce states needed by the actual implementation.

The tutor should not lose track of the current concept, question, diagnosis or learning objective between messages.

A fully real-time autonomous voice agent is not required.

---

# 11. MASTERY TRACKING

The application must distinguish an answer score from demonstrated concept mastery.

## 11.1 Evidence to store

For each attempt, record:

- Learner ID.
- Question ID.
- Concept ID.
- Submitted answer.
- Correctness.
- Reasoning or transcript, where available.
- Diagnosis.
- Evidence supporting the diagnosis.
- Remediation activity.
- Subsequent result.
- Timestamp.

## 11.2 Example mastery policy

A simple prototype policy may use:

- No attempts → `Not assessed`.
- Insufficient attempts → `Developing`.
- Inconsistent results → `Practising`.
- Multiple correct responses across distinct questions, including a transfer question → `Mastered`.

An illustrative threshold is at least four valid attempts across three distinct questions, at least 80% weighted performance, and a correct transfer question.

These thresholds are configurable prototype choices, not validated educational standards.

Correctness and reasoning should both matter. A learner who guesses the correct answer but cannot explain the underlying concept should not automatically be marked as mastered.

Mastery must be recalculated from recorded attempts. Do not increment mastery merely because a lesson was completed.

---

# 12. PRE/POST ASSESSMENT AND REPORTING

Use the same six fixed assessment items for the pre-assessment and post-assessment.

Store each answer separately, linked to its learner, question and assessment phase.

Calculate:

`Assessment percentage = correct answers / total valid questions × 100`

`Score change = post-assessment percentage − pre-assessment percentage`

Example:

- Pre-assessment: 3/6 = 50%.
- Post-assessment: 5/6 = 83.3%.
- Observed change: +33.3 percentage points.
- Complete paired sample size: n = 1.

These numbers are illustrative only.

For multiple learners, report the number with complete paired assessments and the mean paired score change.

Explain that repeating the same items can introduce a practice effect. A small uncontrolled pre/post evaluation does not establish that the tutor caused the improvement.

Never manually enter a result simply to make the dashboard look successful.

---

# 13. SCHEDULED QUIZZES

The full product will support personalised revision schedules.

For the MVP, implement only the simplest reliable version if time allows.

Each review task may contain:

- Learner ID.
- Concept ID.
- Reason for review.
- Due date.
- Status.
- Question IDs.
- Result.

The due date can be determined by a simple rule:

- Repeated misconception → review sooner.
- Weak or inconsistent evidence → review sooner.
- Consistent correct performance → review later.

Do not claim to have implemented a production scheduler if the application only stores a due date.

For the initial demo, a "Due for review" panel that queries saved tasks is sufficient.

---

# 14. TECHNICAL ARCHITECTURE

## Recommended stack

- Language: Python.
- User interface: Streamlit.
- Persistent storage: SQLite.
- Content and rules: JSON.
- AI: one LLM API, if available and permitted.
- Voice: ElevenLabs or another verified speech service.
- Charts: Streamlit charts or Matplotlib.

Keep the backend and frontend in one Python application for the hackathon.

Do not introduce a separate React frontend, Flask backend, Firebase project, or additional database unless the existing codebase already requires it.

## Logical architecture

`Streamlit UI → Learning Controller → Educational Engine → Content Bank / LLM Adapter / SQLite`

The educational engine is responsible for correctness, diagnosis, adaptation, assessment and mastery.

The LLM adapter is responsible for tasks such as natural-language interpretation and grounded conversational phrasing.

The voice adapter handles audio input and output separately.

## Suggested modules

Use these modules if compatible with the existing codebase:

- `app.py` — main Streamlit interface.
- `content.py` — loads approved lessons and questions.
- `diagnosis.py` — misconception rules and classification.
- `tutor.py` — teaching and feedback orchestration.
- `teachback.py` — rubric-based explanation evaluation.
- `mastery.py` — concept mastery calculations.
- `assessment.py` — pre/post assessments and reports.
- `database.py` — persistence and queries.
- `voice.py` — optional speech integration.
- `data/` — JSON lesson and question files.
- `tests/` — validation and workflow tests.

These are suggested responsibilities, not a mandate to reorganise working files.

## Environment variables

Use environment variables for any API credentials, such as:

- `LLM_API_KEY`
- `ELEVENLABS_API_KEY`

The exact names may be adjusted to match the existing implementation.

Store secrets in a local environment file excluded from version control.

The application must handle missing credentials gracefully.

---

# 15. DATABASE DESIGN

Use SQLite with a small schema.

## learners

- `learner_id` — primary key.
- `created_at`.

## attempts

- `attempt_id` — primary key.
- `learner_id`.
- `question_id`.
- `concept_id`.
- `answer`.
- `reasoning`.
- `correct`.
- `diagnosis`.
- `diagnosis_evidence`.
- `activity_id`.
- `timestamp`.

## mastery

- `learner_id`.
- `concept_id`.
- `score`.
- `status`.
- `updated_at`.

Use `(learner_id, concept_id)` as a composite key if appropriate.

Mastery should be reproducible from attempt history.

## assessments

- `assessment_attempt_id`.
- `learner_id`.
- `phase` — pre or post.
- `question_id`.
- `answer`.
- `correct`.
- `timestamp`.

## review_tasks — optional P2

- `task_id`.
- `learner_id`.
- `concept_id`.
- `reason`.
- `due_at`.
- `status`.

Create tables automatically during application startup.

Use parameterised SQL queries. Do not construct SQL by concatenating user input.

For the MVP, a single demo learner or a small number of test learners is sufficient, provided their records are clearly separated.

---

# 16. USER INTERFACE

Build a simple, functional Streamlit interface.

## Screen 1 — Welcome and syllabus

Display:

- Project name.
- Selected subject and chapter.
- Approved concepts.
- Start assessment button.
- A short explanation of the AI tutor's role.

## Screen 2 — Pre-assessment

Display:

- One question at a time.
- Answer choices or text input.
- Submit and next controls.
- Progress indicator.

Persist answers before moving to the next question.

## Screen 3 — Lesson

Display:

- Current concept.
- Explanation.
- Worked example.
- Optional visual.
- Listen button, if implemented.
- Practice question.

## Screen 4 — Diagnostic conversation

Display:

- Student answer.
- Clarifying question, where necessary.
- Diagnosis and evidence in learner-friendly language.
- Targeted activity.
- Follow-up question.

Do not expose technical labels such as M1 or internal confidence values as the primary student-facing feedback.

## Screen 5 — Teach-back

Display:

- Prompt: "Explain what you understood about this topic."
- Text input.
- Microphone control, if implemented.
- Submit explanation button.
- Recording indicator and transcript correction, where supported.

## Screen 6 — Feedback and revision

Display:

- Demonstrated concepts.
- Missing concepts.
- Misunderstandings.
- Rubric score.
- Recommended remedial activity.
- Targeted follow-up quiz.

## Screen 7 — Progress and assessment report

Display:

- Pre/post scores.
- Score change.
- Concept-level mastery.
- Attempts and diagnoses.
- Review tasks, if implemented.
- Sample size and limitations.

Do not hardcode dashboard values.

---

# 17. AI PROMPTING AND OUTPUT VALIDATION

All LLM calls must have a clear responsibility.

Do not ask one unrestricted prompt to teach, diagnose, grade, generate questions, calculate mastery and decide the schedule simultaneously.

## Diagnosis prompt requirements

The model receives:

- Approved question.
- Correct answer.
- Student's answer.
- Student's reasoning.
- Allowed misconception definitions.
- Relevant prior attempts, if needed.

The model must return:

- Correctness interpretation.
- A diagnosis from the allowed list.
- Supporting evidence.
- Whether clarification is required.
- Recommended approved activity.

Validate the output against the schema and allowed IDs.

## Teach-back evaluation prompt requirements

The model receives:

- Approved lesson content.
- Required rubric criteria.
- Student explanation.
- Rules for distinguishing missing from incorrect knowledge.

It must return structured results for every criterion, supporting evidence, an overall explanation, and recommended concepts for revision.

The model must not invent claims about what the student said.

## Teaching prompt requirements

The model receives:

- Approved concept material.
- Student's current learning needs.
- The selected teaching objective.
- An appropriate reading level.

It must produce a clear explanation grounded in that material.

It must not silently introduce concepts outside the approved syllabus.

## Validation requirements

For every structured response:

1. Parse the response.
2. Validate required fields.
3. Check enum values.
4. Reject unknown concept, question or activity IDs.
5. Handle malformed output.
6. Use deterministic fallback behaviour when possible.
7. Record meaningful failures without exposing secrets.

The application must remain usable if the LLM API is unavailable. Predefined lessons, answer checking and core misconception mappings should continue to work.

---

# 18. TESTING AND ACCEPTANCE CRITERIA

The MVP is not complete until these tests pass.

## Test A — Correct answer

Input: A student correctly compares two fractions and provides valid reasoning.

Expected result:

- Answer is marked correct.
- Reasoning is evaluated.
- The attempt is saved.
- Mastery is updated according to the evidence policy.

## Test B — Whole-number bias

Input: "2/5 is larger because five is bigger than three."

Expected result:

- The answer is marked incorrect.
- M1 is selected if supported by the evidence.
- The tutor explains the problem with that reasoning.
- A fraction-strip activity is selected.
- A follow-up question is presented.

## Test C — Different misconception

Input: The student uses a reversed denominator rule.

Expected result:

- The system does not automatically reuse M1.
- M2 is selected only if supported by the reasoning.
- The follow-up activity differs from Test B.

## Test D — Ambiguous answer

Input: The student answers incorrectly but gives no explanation.

Expected result:

- No unsupported diagnosis is assigned.
- The tutor asks a clarifying question.
- The attempt is recorded.

## Test E — Correct answer with invalid reasoning

Input: The student chooses the correct option but explains it using an invalid rule.

Expected result:

- Correctness and conceptual understanding are recorded separately.
- The student is not automatically marked as having mastered the concept.
- A targeted clarification or explanation is provided.

## Test F — Teach-back

Input: The student explains some, but not all, required concepts.

Expected result:

- The rubric evaluates every required criterion.
- The system identifies missing and incorrect ideas separately.
- A targeted revision quiz is generated or selected.

## Test G — Persistence

Action: Submit answers, refresh the page, and reopen the progress view.

Expected result:

- Previously saved answers remain available.
- Mastery is recalculated or retrieved consistently.
- No results are invented or lost.

## Test H — Pre/post reporting

Action: Complete both assessment phases.

Expected result:

- The same six assessment items are used.
- Scores are computed from saved responses.
- Score change is correct.
- The paired sample size is reported accurately.

## Test I — Voice fallback

Action: Deny microphone permission or simulate a voice API failure.

Expected result:

- The app displays a clear message.
- Text input remains available.
- The educational workflow continues.

## Test J — API failure

Action: Simulate an LLM API error.

Expected result:

- The app does not crash.
- Verified content and deterministic question checking remain available.
- The system does not fabricate an AI diagnosis.

---

# 19. SIX-HOUR EXECUTION PLAN

Use this schedule as a prioritisation framework. If less time remains, reduce scope rather than skipping integration testing.

### Phase 1 — First 45 minutes

- Inspect the existing codebase.
- Identify the current working features.
- Confirm available API credentials and dependencies.
- Finalise the JSON structure and shared function contracts.
- Prepare the approved fraction content and question bank.

### Phase 2 — Minutes 45–120

- Implement answer checking.
- Implement misconception mappings.
- Implement uncertainty and clarifying questions.
- Implement activity selection.
- Test two distinct misconceptions.

### Phase 3 — Minutes 120–195

- Build the lesson and quiz interface.
- Implement the diagnostic conversation.
- Implement student teach-back.
- Implement rubric evaluation and targeted feedback.

### Phase 4 — Minutes 195–240

- Add SQLite persistence.
- Implement mastery calculation.
- Implement pre/post assessments.
- Build the score-change report.

### Phase 5 — Minutes 240–300

- Add text-to-speech.
- Add speech-to-text if the selected service supports it.
- Implement microphone controls and fallback behaviour.

### Phase 6 — Minutes 300–360

- Run acceptance tests.
- Fix critical bugs.
- Verify persistence and assessment calculations.
- Rehearse the demonstration.
- Confirm compliance with hackathon rules.

If a feature is incomplete at its allocated checkpoint, prioritise completing the core learning loop over starting another feature.

---

# 20. TEAM COORDINATION

For a four-person beginner team:

**Member 1 — Content and syllabus**

Owns the verified lessons, questions, rubric, and misconception library.

**Member 2 — AI and learning engine**

Owns diagnosis, clarification, adaptive activity selection, and grounded teaching.

**Member 3 — User interface and voice**

Owns Streamlit screens, conversation flow, speech interaction, and visual presentation.

**Member 4 — Data and evaluation**

Owns SQLite, attempt history, mastery calculations, pre/post reports, integration tests, and demo coordination.

Agree on the data contracts before parallel development.

No team member should silently change a shared data structure without communicating it to the others.

Integrate continuously. Do not wait until the final hour to combine separate components.

---

# 21. EXPECTED DEMONSTRATION

The final demonstration should tell one coherent story.

1. A teacher provides or approves the fractions chapter.
2. The student completes a pre-assessment.
3. The tutor identifies a knowledge gap.
4. The tutor teaches the relevant concept.
5. The student answers incorrectly and explains the reasoning.
6. The tutor diagnoses the misconception or asks a clarifying question.
7. The tutor provides a targeted activity.
8. The student explains the topic back to the AI.
9. The tutor evaluates the explanation against the rubric.
10. The student receives targeted revision.
11. The system saves the results and updates concept mastery.
12. The post-assessment report shows the observed score change and limitations.
13. If implemented, the tutor reads an explanation aloud or listens to a spoken answer.

Prepare two different misconception cases so judges can see that the system adapts to reasoning instead of giving identical feedback to everyone.

All displayed results must come from actual recorded interactions or be explicitly labelled as illustrative sample data.

---

# 22. DEFINITION OF DONE

The project is ready for demonstration when:

- The app starts reliably.
- The approved fractions chapter loads.
- The student can complete the pre-assessment.
- Incorrect answers trigger reasoning analysis.
- Ambiguous answers trigger clarification.
- Different supported misconceptions lead to different activities.
- The tutor teaches from verified content.
- The student can explain the topic back to the AI.
- The explanation is evaluated against the rubric.
- Missing concepts trigger targeted revision.
- Attempts persist in SQLite.
- Mastery is based on recorded evidence.
- The same six assessment items can be used for pre/post evaluation.
- The report calculates actual score change and reports the sample size.
- The teacher-support disclaimer is visible.
- Voice works if implemented, with a usable text fallback.
- The core flow survives the acceptance tests.
- AI tools and libraries are disclosed as required by the hackathon rules.

If voice is not completed, the application can still meet the educational objective through text interaction. Do not sacrifice core functionality to make voice work.

---

# 23. DEVELOPMENT RULES FOR FUTURE AI ASSISTANTS

Whenever you receive this project context:

1. Inspect the repository and current implementation first.
2. Determine the remaining time and current working state.
3. List only the missing requirements that matter to the MVP.
4. Prioritise bugs that block the end-to-end learning loop.
5. Propose small, testable implementation steps.
6. Reuse existing files and dependencies where appropriate.
7. Keep mathematical answer checking deterministic.
8. Keep LLM outputs constrained to approved concepts, activities, and schemas.
9. Make persistence and assessment results auditable.
10. Test actual behaviour rather than relying on successful page rendering.
11. Avoid implementing P2 or future features until P0 is complete.
12. Avoid large rewrites unless the current architecture prevents completion.
13. Report completed, incomplete, and untested functionality separately.
14. Provide exact run commands and required environment configuration.
15. If the user requests an additional feature, first explain its impact on the remaining time and whether it threatens the core MVP.

Do not assume that every future feature is part of the current deliverable.

---

# 24. FINAL PRODUCT PRINCIPLE

LearnLoop AI is an evidence-driven, misconception-aware learning system.

Its success does not depend on making the AI sound human or producing a large number of generated quizzes. Its success depends on whether the system can:

- Identify what the learner does and does not understand.
- Support its diagnosis with evidence.
- Ask useful questions when uncertain.
- Adapt instruction to the learner's demonstrated needs.
- Evaluate explanations against clear criteria.
- Track performance over time.
- Report improvement honestly.
- Keep teachers involved in the learning process.

**Immediate implementation priority: complete and test the entire text-based learning loop for one chapter. Then add voice. Then add the simplest useful revision scheduler. Defer everything else.**