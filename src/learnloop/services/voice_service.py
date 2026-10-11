"""ElevenLabs Voice Service with bounded timeouts, fallback discipline, and audit telemetry.

Implements context.md Section 14, 16, 22 and Rule 7:
- Server-side voice proxy
- Strict timeout bound: max 5.0 seconds
- Graceful text fallback whenever credentials are absent, quota exhausted, or network fails
- Operational auditing into `voice_events` table (status, duration_ms, error_code)
"""

import base64
import time
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.orm import Session

from learnloop.config import settings
from learnloop.db.models import VoiceEvent, utc_now


class VoiceService:
    """Manages text-to-speech synthesis and telemetry logging."""

    MAX_TIMEOUT_SECONDS: float = 5.0

    @classmethod
    def synthesize_speech(
        cls,
        db: Session,
        session_id: str,
        text: str,
        interaction_id: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize tutor speech using ElevenLabs with strict 5-second timeout and fallback."""
        clean_text = text.strip()
        target_voice_id = voice_id or settings.elevenlabs_voice_id

        # 1. Audit log: record initial requested event
        event = VoiceEvent(
            session_id=session_id,
            interaction_id=interaction_id,
            provider="elevenlabs",
            direction="text_to_speech",
            status="requested",
            created_at=utc_now(),
        )
        db.add(event)
        db.flush()

        # 2. Check if credentials are configured
        if not settings.elevenlabs_api_key:
            event.status = "failed"
            event.duration_ms = 0
            event.error_code = "VOICE_CREDENTIALS_MISSING"
            db.flush()
            return {
                "status": "fallback",
                "audio_base64": None,
                "mime_type": None,
                "duration_ms": 0,
                "fallback_text": clean_text,
                "message": "Voice synthesis unavailable: no ElevenLabs API key configured. Displaying tutor text.",
                "voice_event_id": event.id,
            }

        # 3. Call ElevenLabs API with strict 5.0s timeout
        start_time = time.monotonic()
        api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice_id}"
        headers = {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": clean_text,
            "model_id": settings.elevenlabs_model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        try:
            with httpx.Client(timeout=cls.MAX_TIMEOUT_SECONDS) as client:
                resp = client.post(api_url, json=payload, headers=headers)
                elapsed_ms = int((time.monotonic() - start_time) * 1000)

                if resp.status_code == 200:
                    event.status = "succeeded"
                    event.duration_ms = elapsed_ms
                    event.error_code = None
                    db.flush()

                    audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                    return {
                        "status": "succeeded",
                        "audio_base64": audio_b64,
                        "mime_type": "audio/mpeg",
                        "duration_ms": elapsed_ms,
                        "fallback_text": clean_text,
                        "message": "Speech synthesized successfully.",
                        "voice_event_id": event.id,
                    }
                else:
                    error_code = (
                        "QUOTA_EXCEEDED"
                        if resp.status_code == 429
                        else f"UPSTREAM_HTTP_{resp.status_code}"
                    )
                    event.status = "failed"
                    event.duration_ms = elapsed_ms
                    event.error_code = error_code
                    db.flush()

                    return {
                        "status": "fallback",
                        "audio_base64": None,
                        "mime_type": None,
                        "duration_ms": elapsed_ms,
                        "fallback_text": clean_text,
                        "message": f"Voice synthesis error ({error_code}). Displaying tutor text.",
                        "voice_event_id": event.id,
                    }

        except httpx.TimeoutException:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            event.status = "failed"
            event.duration_ms = elapsed_ms
            event.error_code = "VOICE_TIMEOUT"
            db.flush()

            return {
                "status": "fallback",
                "audio_base64": None,
                "mime_type": None,
                "duration_ms": elapsed_ms,
                "fallback_text": clean_text,
                "message": "Voice synthesis timed out after 5.0 seconds. Displaying tutor text.",
                "voice_event_id": event.id,
            }
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            event.status = "failed"
            event.duration_ms = elapsed_ms
            event.error_code = "VOICE_NETWORK_ERROR"
            db.flush()

            return {
                "status": "fallback",
                "audio_base64": None,
                "mime_type": None,
                "duration_ms": elapsed_ms,
                "fallback_text": clean_text,
                "message": f"Voice synthesis error ({str(exc)[:50]}). Displaying tutor text.",
                "voice_event_id": event.id,
            }
