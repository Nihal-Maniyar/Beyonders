"""Integration tests for API v1 Socratic tutoring, diagnostic practice, and teach-back endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from learnloop.api.main import app
from learnloop.api.v1.deps import get_db
from learnloop.db.base import Base
from learnloop.db.models import (
    MisconceptionHypothesis,
    ReasoningResponse,
    TutoringInteraction,
)
from learnloop.db.seed import seed_database


@pytest.fixture
def test_setup():
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
        yield client, TestingSessionLocal
    app.dependency_overrides.clear()


@pytest.fixture
def api_client(test_setup):
    client, _ = test_setup
    return client


@pytest.fixture
def db_session(test_setup):
    _, session_factory = test_setup
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def auth_header(api_client):
    res = api_client.post("/api/v1/sessions")
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_practice_diagnose_acceptance_test_a_sound_reasoning(api_client, auth_header, db_session):
    """Acceptance Test A: Correct option with valid reasoning -> NONE diagnosis."""
    res = api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "B",
            "reasoning_text": "Because thirds are bigger pieces than fifths, 2 thirds is greater than 2 fifths.",
        },
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert data["diagnosis_code"] == "NONE"
    assert data["reasoning_status"] == "valid"
    assert data["clarification_required"] is False
    assert "tutor_prompt" in data

    # Check database persistence
    interactions = db_session.query(TutoringInteraction).all()
    assert len(interactions) == 2  # Student response + tutor feedback


def test_practice_diagnose_acceptance_test_b_whole_number_bias_m1(
    api_client, auth_header, db_session
):
    """Acceptance Test B: Whole-number bias M1 correctly classified with remediation hint."""
    res = api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "A",
            "reasoning_text": "2/5 is larger because five is bigger than three.",
        },
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert data["diagnosis_code"] == "M1"
    assert data["next_activity_id"] == "A_FRACTION_STRIPS"

    # Check hypothesis logged
    hyp = db_session.query(MisconceptionHypothesis).filter_by(code="M1").first()
    assert hyp is not None
    assert hyp.status == "tentative"
    assert hyp.confidence >= 0.7


def test_practice_diagnose_acceptance_test_c_reversed_denominator_m2(api_client, auth_header):
    """Acceptance Test C: Reversed denominator M2 rule produces distinct diagnosis & activity."""
    res = api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "A",
            "reasoning_text": "A fraction with a larger denominator is always larger.",
        },
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert data["diagnosis_code"] == "M2"
    assert data["next_activity_id"] == "A_PART_SIZE_EXPLORER"


def test_practice_diagnose_acceptance_test_d_ambiguous_reasoning_u1(api_client, auth_header):
    """Acceptance Test D: Ambiguous reasoning yields U1 with clarifying Socratic question."""
    res = api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "A",
            "reasoning_text": "idk",
        },
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert data["diagnosis_code"] == "U1"
    assert data["clarification_required"] is True
    assert data["clarifying_question"] is not None
    assert len(data["clarifying_question"]) > 10


def test_practice_diagnose_acceptance_test_e_guessed_reasoning(api_client, auth_header):
    """Acceptance Test E: Correct option with guessed reasoning requests clarification."""
    res = api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "B",
            "reasoning_text": "I just guessed randomly",
        },
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert data["reasoning_status"] == "unclear"
    assert data["clarification_required"] is True


def test_teach_back_evaluate_acceptance_test_f_partial_and_full(api_client, auth_header):
    """Acceptance Test F: Teach-back rubric evaluates R1-R5 accurately."""
    # 1. Partial teach-back
    partial_text = (
        "The denominator is the total number of equal parts that a whole is divided into. "
        "The numerator tells how many of those equal-sized pieces we have on our plate."
    )
    res_part = api_client.post(
        "/api/v1/tutoring/teach-back/evaluate",
        json={"explanation": partial_text},
        headers=auth_header,
    )
    assert res_part.status_code == 200
    data_part = res_part.json()
    crit_map = {c["criterion_id"]: c["status"] for c in data_part["criterion_results"]}
    assert crit_map["R1"] == "demonstrated"
    assert crit_map["R2"] == "demonstrated"
    assert crit_map["R4"] == "not_demonstrated"
    assert data_part["earned_points"] >= 2.0

    # 2. Full teach-back
    full_text = (
        "The denominator tells the total number of equal parts in a whole, and numerator counts the pieces. "
        "All parts must be equal-sized fair shares. "
        "Dividing into more pieces makes each piece smaller, so thirds are bigger pieces than fifths. "
        "To compare 2/5 and 2/3 with the same numerator, 2/3 is bigger because thirds are larger parts. "
        "For equivalent fractions, multiply numerator and denominator by the same number."
    )
    res_full = api_client.post(
        "/api/v1/tutoring/teach-back/evaluate",
        json={"explanation": full_text},
        headers=auth_header,
    )
    assert res_full.status_code == 200
    data_full = res_full.json()
    assert data_full["coverage_percent"] == 100.0
    assert data_full["earned_points"] == 5.0


def test_answer_reasoning_submission_and_isolation(api_client, auth_header, db_session):
    """Verify submitting reasoning for an answer persists and enforces session ownership."""
    # 1. Start attempt & submit answer
    def_res = api_client.get("/api/v1/assessments/FRACTIONS_PRE", headers=auth_header).json()
    first_q = def_res["questions"][0]
    q_id = first_q["id"]
    opt_id = first_q["options"][0]["id"]

    start_res = api_client.post(
        "/api/v1/assessments/FRACTIONS_PRE/attempts", headers=auth_header
    ).json()
    att_id = start_res["id"]

    sub_res = api_client.post(
        f"/api/v1/attempts/{att_id}/answers",
        json={"question_id": q_id, "selected_option_id": opt_id},
        headers=auth_header,
    ).json()
    answer_id = sub_res["id"]

    # 2. Submit reasoning
    reason_res = api_client.post(
        f"/api/v1/answers/{answer_id}/reasoning",
        json={"response_text": "Because it is split into 4 equal quarters with 1 shaded."},
        headers=auth_header,
    )
    assert reason_res.status_code == 201
    reason_data = reason_res.json()
    assert reason_data["answer_submission_id"] == answer_id
    assert reason_data["sequence_no"] == 1

    # Verify DB record
    db_reason = (
        db_session.query(ReasoningResponse).filter_by(answer_submission_id=answer_id).first()
    )
    assert db_reason is not None

    # 3. Create Session B and attempt to submit reasoning to Session A's answer -> 403
    session_b_res = api_client.post("/api/v1/sessions").json()
    headers_b = {"Authorization": f"Bearer {session_b_res['token']}"}

    tamper_res = api_client.post(
        f"/api/v1/answers/{answer_id}/reasoning",
        json={"response_text": "Tampered explanation"},
        headers=headers_b,
    )
    assert tamper_res.status_code == 403


def test_tutoring_history_and_misconceptions_retrieval(api_client, auth_header):
    """Verify reading interaction history and active misconception hypotheses."""
    # 1. Practice diagnose with whole number bias
    api_client.post(
        "/api/v1/tutoring/practice/diagnose",
        json={
            "question_code": "Q_C2_PRE_01",
            "student_answer": "A",
            "reasoning_text": "2/5 is larger because five is bigger than three.",
        },
        headers=auth_header,
    )

    # 2. Get history
    hist_res = api_client.get("/api/v1/tutoring/history", headers=auth_header)
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert len(hist) == 2
    assert hist[0]["role"] == "student"
    assert hist[1]["role"] == "tutor"

    # 3. Get misconceptions
    misc_res = api_client.get("/api/v1/tutoring/misconceptions", headers=auth_header)
    assert misc_res.status_code == 200
    miscs = misc_res.json()
    assert len(miscs) == 1
    assert miscs[0]["code"] == "M1"
    assert miscs[0]["status"] == "tentative"
