# LearnLoop AI — Adaptive Fractions Learning Studio

> **VORTEXA 3.0 · Problem Statement E-01**  
> **Chapter Focus:** Comparing Fractions (Grade 4–6 Mathematics, CCSS.MATH.CONTENT.4.NF.A.2)

LearnLoop AI is an educational technology system that investigates **how students reason**, identifies specific mathematical misconceptions, provides targeted visual remediation activities, evaluates student teach-backs against explicit rubrics, and quantifies mastery growth across pre- and post-assessments.

The repository provides two independent, fully functional frontend options:
1. **Primary Frontend:** Modern, tactile **React + Vite** learning studio located in `frontend/`, communicating with a FastAPI backend adapter.
2. **Preserved Backup:** Original interactive **Streamlit** notebook application in `app.py`.

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
- **Interactive Visual Fraction Models**: Tactile, accessible SVG/CSS fraction bars and side-by-side comparative strips with identical-length wholes, letting students visually explore why thirds are wider than fifths ($2/3 > 2/5$).
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
├── frontend/                           # PRIMARY: React + Vite + TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/                 # Button, Card, Badge, Callout
│   │   │   ├── visuals/                # FractionBar, FractionCompare, FractionExplorer
│   │   │   ├── layout/                 # Header, StageStepper, AppShell
│   │   │   └── views/                  # 8 Stage Views (Welcome, PreTest, Lesson, Practice, etc.)
│   │   ├── design/                     # theme.css (tactile studio tokens, typography)
│   │   ├── services/api.ts             # Type-safe API client communicating with backend
│   │   └── types/index.ts              # TypeScript schemas matching backend models
│   ├── package.json
│   └── vite.config.ts                  # Vite config with /api proxy to FastAPI
├── src/
│   └── learnloop/
│       ├── api/                        # FastAPI REST API adapter for React frontend
│       │   ├── main.py                 # App entry point, CORS middleware, lifespan
│       │   └── routes.py               # REST endpoints for assessment, diagnosis, teach-back
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
│   ├── api/                            # FastAPI endpoint and student journey tests
│   ├── unit/                           # Isolated domain rule and content tests
│   ├── integration/                    # Service, persistence isolation, and session tests
│   └── ui/                             # Headless AppTest UI workflow tests
├── app.py                              # BACKUP: Preserved Streamlit interactive app
├── requirements.txt                    # Production runtime dependencies
├── requirements-dev.txt                # Development and testing dependencies
├── pyproject.toml                      # Project metadata, pytest, and ruff configuration
└── .github/workflows/ci.yml            # Automated CI workflow
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ (tested on Python 3.9, 3.10, and 3.11)
- Node.js 18+ and npm
- Git

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Nihal-Maniyar/Beyonders.git
cd Beyonders

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python backend dependencies
pip install -r requirements-dev.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## 💻 Running the Applications

### Option A: Primary React + Vite Application (Recommended)

1. **Start the FastAPI Backend** (Terminal 1):
   ```bash
   uvicorn src.learnloop.api.main:app --port 8000 --reload
   ```
   *FastAPI docs will be available at `http://localhost:8000/docs`.*

2. **Start the React Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```
   *Open your browser at **`http://localhost:5173`**.*

---

### Option B: Preserved Streamlit Backup Application

To run the original self-contained Streamlit application:

```bash
streamlit run app.py
```
*Open your browser at **`http://localhost:8501`**.*

Both applications connect to the same educational domain engine and SQLite persistence layer.

---

## 🧪 Running Tests & Quality Checks

The repository includes a comprehensive 46-test suite spanning API, unit, integration, and UI acceptance flows, plus frontend build verification.

### Run All Python Tests
```bash
pytest -v
```

### Run Python Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Python Linter and Formatter
```bash
ruff check .
ruff format --check .
```

### Build & Type-Check Frontend
```bash
cd frontend
npm run build
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

- **Phases 0–5 Complete**: Baseline content bank, domain diagnosis, rubric evaluator, database persistence, interactive 8-stage UI workflows (React and Streamlit), comprehensive edge-case tests, and CI automation.
- **Phase 6 AI Enhancements Deferred**: Optional LLM-assisted conversational expansion (Anthropic/OpenAI/Gemini) and ElevenLabs voice narration are architecturally isolated and deferred to Phase 6. The entire educational platform is fully functional and self-contained without them.
