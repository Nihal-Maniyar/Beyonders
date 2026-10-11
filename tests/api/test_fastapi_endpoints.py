"""Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import learnloop.db.models  # noqa: F401
from learnloop.api.main import app
from learnloop.api.routes import get_db
from learnloop.db.base import Base


@pytest.fixture
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_api_health(client_with_db):
    response = client_with_db.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Fractions" in data["chapter_loaded"]


def test_get_chapter_syllabus(client_with_db):
    response = client_with_db.get("/api/chapter")
    assert response.status_code == 200
    data = response.json()
    assert data["chapter_id"] == "CH_FRACTIONS_01"
    assert len(data["concepts"]) == 3
    concept_ids = [c["concept_id"] for c in data["concepts"]]
    assert concept_ids == ["C1", "C2", "C3"]


def test_get_fixed_assessment_questions_are_confidential(client_with_db):
    """Verify fixed assessment questions scrub answers and explanations."""
    response = client_with_db.get("/api/assessment/fixed")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 6
    for q in questions:
        # Crucial: correct_answer and verified_explanation MUST be blank for student integrity!
        assert q["correct_answer"] == ""
        assert q["verified_explanation"] == ""
        assert q["misconception_mappings"] == {}


def test_learner_session_creation(client_with_db):
    response = client_with_db.post(
        "/api/learners/session",
        json={"learner_id": "api_test_student_01", "display_name": "Maya"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["learner_id"] == "api_test_student_01"
    assert data["display_name"] == "Maya"
    assert data["session_id"] is not None


def test_diagnostic_practice_api(client_with_db):
    # Student answers Q_C2_PRE_01 with whole-number bias reasoning
    response = client_with_db.post(
        "/api/practice/diagnose",
        json={
            "learner_id": "api_student_m1",
            "question_id": "Q_C2_PRE_01",
            "student_answer": "A",
            "reasoning_text": "2/5 is bigger because five is bigger than three.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["diagnosis_code"] == "M1"
    assert data["next_activity_id"] == "A_FRACTION_STRIPS"
    assert "strip" in data["student_feedback"].lower()


def test_teachback_evaluation_api(client_with_db):
    response = client_with_db.post(
        "/api/teachback/evaluate",
        json={
            "learner_id": "api_student_tb",
            "explanation": (
                "The denominator is the total number of equal parts. The numerator is how many parts are counted. "
                "Fractions must always be equal sized fair shares. When denominator is bigger, each slice is smaller. "
                "Thirds are larger than fifths. Equivalent fractions scale by multiplying top and bottom."
            ),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["earned_points"] >= 4.0
    assert data["coverage_percent"] >= 80.0
    assert len(data["criterion_results"]) == 5
