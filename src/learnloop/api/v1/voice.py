"""API endpoints for ElevenLabs voice synthesis and text fallback.

Implements:
- POST /api/v1/voice/synthesize
- GET  /api/v1/voice/events
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession, VoiceEvent
from learnloop.services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["Voice Synthesis"])


class VoiceSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text for voice synthesis")
    interaction_id: Optional[str] = Field(None, description="Optional tutoring interaction ID")
    voice_id: Optional[str] = Field(None, description="Optional custom ElevenLabs voice ID")


class VoiceSynthesizeResponse(BaseModel):
    status: str
    audio_base64: Optional[str] = None
    mime_type: Optional[str] = None
    duration_ms: int
    fallback_text: str
    message: str
    voice_event_id: str


class VoiceEventItem(BaseModel):
    id: str
    status: str
    direction: str
    duration_ms: Optional[int]
    error_code: Optional[str]
    created_at: str


@router.post(
    "/synthesize",
    response_model=VoiceSynthesizeResponse,
    status_code=status.HTTP_200_OK,
)
def synthesize_tutor_voice(
    payload: VoiceSynthesizeRequest,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Synthesize tutor speech via server-side ElevenLabs proxy.

    Never exposes provider secrets to client. Enforces strict 5-second timeout
    and returns a graceful text fallback whenever voice is unconfigured or failing.
    """
    result = VoiceService.synthesize_speech(
        db=db,
        session_id=current_session.id,
        text=payload.text,
        interaction_id=payload.interaction_id,
        voice_id=payload.voice_id,
    )
    db.commit()
    return result


@router.get(
    "/events",
    response_model=List[VoiceEventItem],
    status_code=status.HTTP_200_OK,
)
def get_voice_audit_events(
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve operational telemetry and audit logs for the current session's voice requests."""
    events = (
        db.query(VoiceEvent)
        .filter(VoiceEvent.session_id == current_session.id)
        .order_by(VoiceEvent.created_at.desc())
        .all()
    )
    return [
        {
            "id": ev.id,
            "status": ev.status,
            "direction": ev.direction,
            "duration_ms": ev.duration_ms,
            "error_code": ev.error_code,
            "created_at": ev.created_at.isoformat(),
        }
        for ev in events
    ]
