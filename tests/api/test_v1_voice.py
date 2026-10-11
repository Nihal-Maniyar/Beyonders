"""Integration tests for /api/v1/voice endpoints, timeout limits, fallback discipline, and audit logs."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from learnloop.api.main import app
from learnloop.api.v1.deps import get_db
from learnloop.config import settings
from learnloop.db.base import Base
from learnloop.db.models import VoiceEvent
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


def test_voice_synthesize_graceful_fallback_when_credentials_missing(
    api_client, auth_header, db_session, monkeypatch
):
    """Verify that when ELEVENLABS_API_KEY is not set, API returns graceful text fallback without crashing."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", None)

    sample_text = "Let's look at fractions together! Thirds are bigger pieces than fifths."
    res = api_client.post(
        "/api/v1/voice/synthesize",
        json={"text": sample_text},
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "fallback"
    assert data["audio_base64"] is None
    assert data["fallback_text"] == sample_text
    assert "no ElevenLabs API key" in data["message"]
    assert "voice_event_id" in data

    # Verify audit event in DB
    event = db_session.query(VoiceEvent).filter_by(id=data["voice_event_id"]).first()
    assert event is not None
    assert event.status == "failed"
    assert event.error_code == "VOICE_CREDENTIALS_MISSING"


def test_voice_synthesize_success_mocked(api_client, auth_header, db_session, monkeypatch):
    """Verify that when ElevenLabs responds successfully, audio base64 is returned and audit logged."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", "mock-valid-api-key-12345")

    mock_audio_bytes = b"\xff\xfb\x90\x44" + b"fake-audio-payload"
    mock_resp = httpx.Response(
        200, content=mock_audio_bytes, request=httpx.Request("POST", "https://api.elevenlabs.io")
    )

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("learnloop.services.voice_service.httpx.Client", return_value=mock_client):
        res = api_client.post(
            "/api/v1/voice/synthesize",
            json={"text": "Thirds are bigger pieces than fifths."},
            headers=auth_header,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "succeeded"
        assert data["audio_base64"] is not None
        assert data["mime_type"] == "audio/mpeg"
        assert data["duration_ms"] >= 0

        # Verify audit event in DB
        event = db_session.query(VoiceEvent).filter_by(id=data["voice_event_id"]).first()
        assert event is not None
        assert event.status == "succeeded"
        assert event.error_code is None


def test_voice_synthesize_timeout_fallback(api_client, auth_header, db_session, monkeypatch):
    """Verify that a timeout on ElevenLabs returns graceful fallback within 5.0 seconds."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", "mock-key")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out after 5.0s")

    with patch("learnloop.services.voice_service.httpx.Client", return_value=mock_client):
        res = api_client.post(
            "/api/v1/voice/synthesize",
            json={"text": "Explaining numerator and denominator."},
            headers=auth_header,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "fallback"
        assert data["audio_base64"] is None
        assert "timed out" in data["message"].lower()

        # Check DB audit status
        event = db_session.query(VoiceEvent).filter_by(id=data["voice_event_id"]).first()
        assert event is not None
        assert event.status == "failed"
        assert event.error_code == "VOICE_TIMEOUT"


def test_voice_events_audit_and_session_isolation(api_client, auth_header, monkeypatch):
    """Verify GET /api/v1/voice/events returns session telemetry and isolates across learners."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", None)

    # 1. Session A generates a voice event
    api_client.post(
        "/api/v1/voice/synthesize",
        json={"text": "Session A tutor text."},
        headers=auth_header,
    )

    events_a = api_client.get("/api/v1/voice/events", headers=auth_header).json()
    assert len(events_a) == 1
    assert events_a[0]["error_code"] == "VOICE_CREDENTIALS_MISSING"

    # 2. Session B inspects its events -> empty
    session_b_res = api_client.post("/api/v1/sessions").json()
    headers_b = {"Authorization": f"Bearer {session_b_res['token']}"}

    events_b = api_client.get("/api/v1/voice/events", headers=headers_b).json()
    assert len(events_b) == 0


def test_voice_transcribe_fallback_when_credentials_missing(
    api_client, auth_header, db_session, monkeypatch
):
    """Verify that when ELEVENLABS_API_KEY is not set, transcribe returns graceful text fallback without crashing."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", None)

    fake_audio = b"\x1a\x45\xdf\xa3fake-audio-chunk"
    files = {"file": ("recording.webm", fake_audio, "audio/webm")}
    res = api_client.post(
        "/api/v1/voice/transcribe",
        files=files,
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "fallback"
    assert data["text"] == ""
    assert "no ElevenLabs API key" in data["message"]
    assert "voice_event_id" in data

    # Verify audit event in DB
    event = db_session.query(VoiceEvent).filter_by(id=data["voice_event_id"]).first()
    assert event is not None
    assert event.direction == "speech_to_text"
    assert event.status == "failed"
    assert event.error_code == "VOICE_CREDENTIALS_MISSING"


def test_voice_transcribe_success_mocked(api_client, auth_header, db_session, monkeypatch):
    """Verify that when ElevenLabs STT responds successfully, text is returned and audited."""
    monkeypatch.setattr(settings, "elevenlabs_api_key", "mock-valid-api-key-12345")

    mock_resp = httpx.Response(
        200,
        json={"text": "Thirds are bigger pieces than fifths.", "language_code": "en"},
        request=httpx.Request("POST", "https://api.elevenlabs.io/v1/speech-to-text"),
    )

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    fake_audio = b"\x1a\x45\xdf\xa3fake-audio-chunk"
    files = {"file": ("recording.webm", fake_audio, "audio/webm")}

    with patch("learnloop.services.voice_service.httpx.Client", return_value=mock_client):
        res = api_client.post(
            "/api/v1/voice/transcribe",
            files=files,
            headers=auth_header,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "succeeded"
        assert data["text"] == "Thirds are bigger pieces than fifths."
        assert data["duration_ms"] >= 0

        # Verify audit event in DB
        event = db_session.query(VoiceEvent).filter_by(id=data["voice_event_id"]).first()
        assert event is not None
        assert event.direction == "speech_to_text"
        assert event.status == "succeeded"
        assert event.error_code is None


def test_voice_transcribe_empty_file_rejected(api_client, auth_header):
    """Verify that uploading an empty audio file returns 400 Bad Request."""
    files = {"file": ("recording.webm", b"", "audio/webm")}
    res = api_client.post(
        "/api/v1/voice/transcribe",
        files=files,
        headers=auth_header,
    )
    assert res.status_code == 400
