"""Integration tests for /api/v1/assessments and /api/v1/attempts endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from learnloop.api.main import app
from learnloop.api.v1.deps import get_db
from learnloop.db.base import Base
from learnloop.db.seed import seed_database


@pytest.fixture
def api_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as s:
        seed_database(s)
        s.commit()

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


@pytest.fixture
def auth_header(api_client):
    res = api_client.post("/api/v1/sessions")
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_assessment_definition_never_leaks_answer_keys(api_client, auth_header):
    """Verify GET /api/v1/assessments/{code} returns safe question content without is_correct."""
    res = api_client.get("/api/v1/assessments/FRACTIONS_PRE", headers=auth_header)
    assert res.status_code == 200
    data = res.json()

    assert data["code"] == "FRACTIONS_PRE"
    assert len(data["questions"]) == 6

    # Verify no option contains 'is_correct' or explanation
    for q in data["questions"]:
        assert "prompt" in q
        assert len(q["options"]) == 4
        for opt in q["options"]:
            assert "is_correct" not in opt
            assert "option_key" in opt
            assert "option_text" in opt


def test_full_attempt_submission_and_scoring_flow(api_client, auth_header):
    """Verify start attempt -> submit answers -> complete attempt -> score calculated."""
    # 1. Fetch questions to get IDs and options
    def_res = api_client.get("/api/v1/assessments/FRACTIONS_PRE", headers=auth_header)
    questions = def_res.json()["questions"]

    # 2. Start attempt
    start_res = api_client.post("/api/v1/assessments/FRACTIONS_PRE/attempts", headers=auth_header)
    assert start_res.status_code == 201
    attempt_id = start_res.json()["id"]

    # 3. Submit an answer for each question
    for q in questions:
        opt_id = q["options"][0]["id"]  # Pick first option
        ans_res = api_client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={"question_id": q["id"], "selected_option_id": opt_id},
            headers=auth_header,
        )
        assert ans_res.status_code == 200

    # 4. Complete attempt
    comp_res = api_client.post(f"/api/v1/attempts/{attempt_id}/complete", headers=auth_header)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["status"] == "completed"
    assert comp_data["raw_score"] is not None
    assert comp_data["max_score"] == 6.0

    # 5. Idempotent completion check
    repeat_res = api_client.post(f"/api/v1/attempts/{attempt_id}/complete", headers=auth_header)
    assert repeat_res.status_code == 200
    assert repeat_res.json()["raw_score"] == comp_data["raw_score"]


def test_attempt_completion_rejected_when_unanswered_questions_remain(api_client, auth_header):
    """Verify completing an attempt fails if required questions are unanswered."""
    start_res = api_client.post("/api/v1/assessments/FRACTIONS_PRE/attempts", headers=auth_header)
    attempt_id = start_res.json()["id"]

    # Attempt to complete immediately with 0 answers submitted
    comp_res = api_client.post(f"/api/v1/attempts/{attempt_id}/complete", headers=auth_header)
    assert comp_res.status_code == 400
    assert comp_res.json()["error"]["code"] == "COMPLETION_ERROR"
