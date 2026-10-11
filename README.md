# LearnLoop AI — Adaptive AI Tutor & Misconception Detector

> **VORTEXA 3.0 · Problem Statement E-01**  
> **Chapter Focus:** Comparing Fractions (Grade 4–6 Mathematics, CCSS.MATH.CONTENT.4.NF.A.2)

LearnLoop AI is an educational technology system that investigates **how students reason**, identifies specific mathematical misconceptions, provides targeted remedial activities, evaluates student teach-backs against explicit rubrics, and quantifies mastery growth across pre- and post-assessments.

---

## 🎯 Key Capabilities

- **8-Stage Student Learning Workflow**: A complete notebook-themed learning journey from syllabus review to baseline pre-assessment, concept lessons, interactive diagnostic practice, guided remediation, teach-back evaluation, post-assessment, and mastery progress reporting.
- **Deterministic Misconception Engine**: Diagnoses student thinking into validated taxonomy codes:
  - **M1**: Whole-Number Bias (e.g., believing $2/5 > 2/3$ because $5 > 3$)
  - **M2**: Reversed Denominator Rule (believing larger denominators mean larger parts)
  - **M3**: Numerator-Only Comparison (comparing top numbers while ignoring denominators)
  - **M4**: Invalid Additive Transformation (believing adding the same number preserves equivalence)
  - **S1**: Arithmetic Slip (correct conceptual strategy with calculation error)
  - **U1**: Unclear / Ambiguous Reasoning (triggers Socratic clarifying questions)
  - **NONE**: Sound mathematical reasoning
- **Rubric-Grounded Teach-Back Evaluation**: Grades student explanations against 5 standardized criteria ($R1$–$R5$) with point awards (1.0 demonstrated, 0.5 partial, 0.0 incorrect/not demonstrated) and percentage coverage.
- **Mastery Tracking**: Evaluates skill acquisition based on evidence:
  - Requires at least 2 distinct correct questions and successful transfer item execution to achieve `MASTERED`.
  - Repeated answers to the same question do not artificially inflate mastery scores.
- **Pre-to-Post Assessment Reporting**: Measures paired learning gains between baseline and post-learning runs, reporting percentage points change and concept-level mastery delta.
- **Spaced Review Scheduling**: Generates actionable revision tasks whenever misconceptions are detected.
- **Offline Reliability & Zero Credentials Required**: The core educational loop, diagnostic engine, rubric evaluator, database persistence, and test suite operate 100% offline with zero external API dependencies.

---

## 🏗️ Architecture & Project Structure

```text
beyonders/
├── data/                               # Verified Curriculum Content Bank
│   ├── fractions_chapter.json          # Chapter syllabus and concept definitions (C1, C2, C3)
│   ├── questions.json                  # Pre/post/practice questions with misconception maps
│   ├── activities.json                 # Remediation activities mapped to diagnosis codes
│   └── rubric.json                     # Teach-back rubric criteria (R1–R5)
├── src/
│   └── learnloop/
│       ├── config.py                   # Pydantic v2 application settings
│       ├── content/                    # Content loader and integrity validator
│       ├── db/                         # SQLAlchemy 2.0 Base, engine, and ORM models
│       ├── domain/                     # Pure educational domain logic & business rules
│       │   ├── diagnosis_rules.py      # Deterministic misconception diagnosis engine
│       │   ├── teachback_rules.py      # Rubric evaluation engine (R1–R5)
│       │   ├── mastery_rules.py        # Mastery status and evidence aggregation
│       │   └── assessment_rules.py     # Pre-post paired gain scoring
│       ├── repositories/               # Persistence repositories (Learners, Attempts, etc.)
│       ├── services/                   # Application orchestration services
│       └── ui/                         # Streamlit UI theme and notebook components
├── tests/
│   ├── unit/                           # Isolated domain rule and content tests
│   ├── integration/                    # Service, persistence isolation, and session tests
│   └── ui/                             # Headless AppTest UI workflow tests
├── app.py                              # Main interactive Streamlit application
├── requirements.txt                    # Production runtime dependencies
├── requirements-dev.txt                # Development and testing dependencies
├── pyproject.toml                      # Project metadata, pytest, and ruff configuration
└── .github/workflows/ci.yml            # Automated CI workflow
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ (tested on Python 3.9, 3.10, and 3.11)
- Git

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Nihal-Maniyar/Beyonders.git
cd Beyonders

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Run the Interactive Application

```bash
# Start Streamlit application
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running Tests & Quality Checks

The repository includes a comprehensive 39-test suite spanning unit, integration, and UI acceptance flows.

### Run All Tests
```bash
pytest -v
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Linter and Formatter
```bash
# Check code style and imports
ruff check .

# Check formatting
ruff format --check .

# Auto-fix formatting if needed
ruff format .
```

---

## 💾 Database Persistence & Data Safety

- **Default Engine**: Local SQLite database (`learnloop.db`), automatically created on first run.
- **Test Isolation**: All test suites utilize in-memory SQLite (`sqlite:///:memory:`) or isolated temporary database files, ensuring tests never overwrite production or development data.
- **Production PostgreSQL Compatibility**: All models are built with standard SQLAlchemy 2.0 ORM types (`UUID`, `DateTime(timezone=True)`, `JSON`, `ForeignKey`), ready for PostgreSQL deployment by updating `LEARNLOOP_DATABASE_URL` in the environment.
- **Transaction Rollback**: Data modifications are executed with transactional safety; mid-operation errors trigger automatic rollback without partial data corruption.

---

## 📚 Curriculum Standards Alignment

| Concept Code | Title | Target Learning Objective | Standards |
| :--- | :--- | :--- | :--- |
| **C1** | Understanding Fractions | Parts of a whole, fair shares, equal sizing | CCSS.MATH.4.NF.A.1 |
| **C2** | Comparing Fractions | Common numerators, denominators, and benchmark reasoning | CCSS.MATH.4.NF.A.2 |
| **C3** | Equivalent Fractions | Multiplicative scaling vs. invalid additive alterations | CCSS.MATH.4.NF.A.1 |

---

## 🛡️ Limitations & Phase Scope

- **Phase 0–5 Complete**: Baseline content bank, domain diagnosis, rubric evaluator, database persistence, interactive 8-stage UI workflow, comprehensive edge-case tests, and CI automation.
- **Phase 6 AI Enhancements Deferred**: Optional LLM-assisted conversational expansion (Anthropic/OpenAI/Gemini) and ElevenLabs voice narration are architecturally isolated and deferred to Phase 6. The entire educational platform is fully functional and self-contained without them.
