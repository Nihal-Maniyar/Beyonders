"""Integration tests for /api/v1/sessions anonymous session authentication."""

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
def client_with_memory_db():
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


def test_create_anonymous_session_returns_token_and_cookie(client_with_memory_db):
    """Verify session creation returns secret token in header/body and sets HttpOnly cookie."""
    res = client_with_memory_db.post("/api/v1/sessions")
    assert res.status_code == 201
    data = res.json()

    assert "session" in data
    assert "id" in data["session"]
    assert data["session"]["status"] == "active"
    assert "token" in data
    assert len(data["token"]) >= 32

    # Verify cookie and header
    assert "session_token" in res.cookies
    assert "X-Session-Token" in res.headers


def test_get_current_session_authenticated(client_with_memory_db):
    """Verify accessing /api/v1/sessions/current with valid token returns session metadata."""
    create_res = client_with_memory_db.post("/api/v1/sessions")
    token = create_res.json()["token"]
    session_id = create_res.json()["session"]["id"]

    # 1. Access using Bearer Authorization header
    res_auth = client_with_memory_db.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["session"]["id"] == session_id

    # 2. Access using X-Session-Token header
    res_hdr = client_with_memory_db.get(
        "/api/v1/sessions/current",
        headers={"X-Session-Token": token},
    )
    assert res_hdr.status_code == 200
    assert res_hdr.json()["session"]["id"] == session_id


def test_missing_or_invalid_token_returns_401(client_with_memory_db):
    """Verify accessing protected routes without token or with forged token yields HTTP 401."""
    # No token
    res_missing = client_with_memory_db.get("/api/v1/sessions/current")
    assert res_missing.status_code == 401
    assert res_missing.json()["error"]["code"] == "MISSING_SESSION_TOKEN"

    # Forged token
    res_invalid = client_with_memory_db.get(
        "/api/v1/sessions/current",
        headers={"Authorization": "Bearer forged-fake-token-xyz"},
    )
    assert res_invalid.status_code == 401
    assert res_invalid.json()["error"]["code"] == "INVALID_OR_EXPIRED_SESSION"


def test_delete_current_session(client_with_memory_db):
    """Verify deleting session marks it completed and clears cookie."""
    create_res = client_with_memory_db.post("/api/v1/sessions")
    token = create_res.json()["token"]

    del_res = client_with_memory_db.delete(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200

    # Next attempt to use same token fails because session is completed
    check_res = client_with_memory_db.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert check_res.status_code == 401
