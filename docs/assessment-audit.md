# LearnLoop AI — Assessment Question Bank & Confidentiality Audit

> **Document Status:** Verified  
> **Source of Truth:** [`context.md`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/context.md) Section 7, 16, 22  
> **Target Question Bank:** [`data/questions.json`](file:///c:/Users/prade/OneDrive/Desktop/Beyonders/data/questions.json)

---

## 1. Benchmark Assessment Structure

The diagnostic pre-assessment (`FRACTIONS_PRE`) and post-assessment (`FRACTIONS_POST`) utilize the approved 6-question benchmark suite to measure conceptual growth:

| Code | Concept | Question Prompt Summary | Difficulty | Focus Area |
| :--- | :--- | :--- | :--- | :--- |
| `Q_C1_PRE_01` | C1 | Which shape shows 1/4 shaded? (Equal parts test) | Easy | Fair shares vs unequal pieces |
| `Q_C1_PRE_02` | C1 | In 3/5, what does 5 represent? | Easy | Role of the denominator |
| `Q_C2_PRE_01` | C2 | Which is larger: 2/5 or 2/3? | Medium | Common numerator comparison |
| `Q_C2_PRE_02` | C2 | Order unit fractions 1/8, 1/3, 1/5 from least to greatest | Medium | Inverse part-size principle |
| `Q_C3_PRE_01` | C3 | Which fraction is equivalent to 1/2? | Easy | Multiplicative scaling |
| `Q_C3_PRE_02` | C3 | Why are 2/3 and 4/6 equivalent? | Medium | Proportional equality |

---

## 2. Assessment Confidentiality Guarantee

To guarantee assessment integrity and eliminate client-side cheating:

1. **Answer Key Scrubbing:**  
   The public endpoint `GET /api/v1/assessments/{code}` returns question prompts and option choices (`option_key`, `option_text`), but **never** includes `is_correct`, explanations, points awarded, or misconception mappings.
   
2. **Server-Side Scoring:**  
   Submissions sent via `POST /api/v1/attempts/{attempt_id}/answers` contain only `question_id` and the learner's choice. Correctness and score calculations are executed purely server-side during `POST /api/v1/attempts/{attempt_id}/complete`.

3. **Confidentiality Automated Test Evidence:**  
   Verified in `tests/api/test_v1_assessments.py::test_get_assessment_definition_never_leaks_answer_keys` and `tests/unit/test_edge_cases_educational.py::test_pre_assessment_content_confidentiality_guarantee`.

---

## 3. Practice & Transfer Question Inventory

In addition to the 6 benchmark questions, the question bank includes targeted practice and transfer questions:
- `Q_C1_PRAC_01`: Identifying equal-sized parts on irregular shapes.
- `Q_C2_PRAC_01`: Comparing fractions with identical numerators using visual strips.
- `Q_C3_PRAC_01`: Finding equivalent fractions by multiplying numerator and denominator.
- `Q_C2_TRANSFER_01`: Transfer question applying inverse denominator principles in an unfamiliar sharing context.

---

## 4. Scoring Algorithm Verification

- **Points Per Question:** Default 1.0 point per benchmark question. Total possible: 6.0 points.
- **Percentage Score:** $\text{Score \%} = \frac{\text{Earned Points}}{\text{Max Points}} \times 100.0$
- **Growth Delta:** Calculated as $\text{Post-Assessment \%} - \text{Pre-Assessment \%}$ in percentage points (pp).
- **Idempotency:** Re-invoking complete on an already finalized attempt returns historical scores without modifying the database or double-counting.

