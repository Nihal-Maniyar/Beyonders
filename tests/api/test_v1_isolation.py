"""Integration tests verifying strict multi-tenant anonymous session isolation."""

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


def test_cross_session_isolation_attempts_and_answers(api_client):
    """Verify Session B cannot read, answer, or complete an attempt owned by Session A."""
    # 1. Create Session A and Session B
    res_a = api_client.post("/api/v1/sessions")
    token_a = res_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    res_b = api_client.post("/api/v1/sessions")
    token_b = res_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. Session A starts an attempt
    start_res = api_client.post("/api/v1/assessments/FRACTIONS_PRE/attempts", headers=headers_a)
    attempt_a_id = start_res.json()["id"]

    # 3. Session B attempts to read Session A's attempt -> 404
    read_res = api_client.get(f"/api/v1/attempts/{attempt_a_id}", headers=headers_b)
    assert read_res.status_code == 404

    # 4. Session B attempts to submit an answer to Session A's attempt -> 403
    def_res = api_client.get("/api/v1/assessments/FRACTIONS_PRE", headers=headers_b)
    q1 = def_res.json()["questions"][0]

    sub_res = api_client.post(
        f"/api/v1/attempts/{attempt_a_id}/answers",
        json={
            "question_id": q1["id"],
            "selected_option_id": q1["options"][0]["id"],
        },
        headers=headers_b,
    )
    assert sub_res.status_code == 403

    # 5. Session B attempts to complete Session A's attempt -> 403
    comp_res = api_client.post(f"/api/v1/attempts/{attempt_a_id}/complete", headers=headers_b)
    assert comp_res.status_code == 403

    # 6. Session B checks progress -> sees no completed attempts
    prog_res = api_client.get("/api/v1/progress", headers=headers_b)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert prog_data["pre_assessment"]["completed"] is False
