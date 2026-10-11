"""Integration tests for /api/v1/lessons and /api/v1/progress endpoints."""

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


def test_list_lessons_and_get_detail(api_client, auth_header):
    """Verify listing published lessons and fetching lesson details."""
    res = api_client.get("/api/v1/lessons", headers=auth_header)
    assert res.status_code == 200
    lessons = res.json()
    assert len(lessons) == 3
    assert lessons[0]["sequence_no"] == 1

    # Fetch detail
    lesson_id = lessons[0]["id"]
    detail_res = api_client.get(f"/api/v1/lessons/{lesson_id}", headers=auth_header)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == lessons[0]["title"]
    assert len(detail["concepts"]) >= 1
    assert detail["concepts"][0]["code"] == "C1"


def test_progress_report_pre_and_post_comparison(api_client, auth_header):
    """Verify progress report calculates comparison when pre and post assessments are completed."""
    # 1. Complete Pre-Assessment
    def_pre = api_client.get("/api/v1/assessments/FRACTIONS_PRE", headers=auth_header).json()
    start_pre = api_client.post(
        "/api/v1/assessments/FRACTIONS_PRE/attempts", headers=auth_header
    ).json()
    for q in def_pre["questions"]:
        api_client.post(
            f"/api/v1/attempts/{start_pre['id']}/answers",
            json={"question_id": q["id"], "selected_option_id": q["options"][0]["id"]},
            headers=auth_header,
        )
    api_client.post(f"/api/v1/attempts/{start_pre['id']}/complete", headers=auth_header)

    # 2. Complete Post-Assessment
    def_post = api_client.get("/api/v1/assessments/FRACTIONS_POST", headers=auth_header).json()
    start_post = api_client.post(
        "/api/v1/assessments/FRACTIONS_POST/attempts", headers=auth_header
    ).json()
    for q in def_post["questions"]:
        api_client.post(
            f"/api/v1/attempts/{start_post['id']}/answers",
            json={"question_id": q["id"], "selected_option_id": q["options"][0]["id"]},
            headers=auth_header,
        )
    api_client.post(f"/api/v1/attempts/{start_post['id']}/complete", headers=auth_header)

    # 3. Check progress
    prog_res = api_client.get("/api/v1/progress", headers=auth_header)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()

    assert prog_data["pre_assessment"]["completed"] is True
    assert prog_data["post_assessment"]["completed"] is True
    assert prog_data["comparison"]["is_comparable"] is True
    assert isinstance(prog_data["comparison"]["percentage_point_change"], float)
