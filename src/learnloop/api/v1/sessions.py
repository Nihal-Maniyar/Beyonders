"""Anonymous session management API endpoints."""

import datetime

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession
from learnloop.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionDetail(BaseModel):
    id: str
    status: str
    created_at: datetime.datetime
    expires_at: datetime.datetime


class SessionCreateResponse(BaseModel):
    session: SessionDetail
    token: str


class SessionCurrentResponse(BaseModel):
    session: SessionDetail


@router.post("", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_session(response: Response, db: Session = Depends(get_db)):
    """Initialize a new anonymous learning session with a high-entropy secret token."""
    session_obj, raw_token = SessionService.create_session(db)

    # Set secure HttpOnly cookie for browser clients
    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        samesite="lax",
        max_age=86400,
    )
    # Also expose token in custom header for programmatic / mobile clients
    response.headers["X-Session-Token"] = raw_token

    return {
        "session": {
            "id": session_obj.id,
            "status": session_obj.status,
            "created_at": session_obj.created_at,
            "expires_at": session_obj.expires_at,
        },
        "token": raw_token,
    }


@router.get("/current", response_model=SessionCurrentResponse)
def get_current_session_info(
    current_session: LearningSession = Depends(get_current_session),
):
    """Retrieve details and remaining validity of the active anonymous session."""
    return {
        "session": {
            "id": current_session.id,
            "status": current_session.status,
            "created_at": current_session.created_at,
            "expires_at": current_session.expires_at,
        }
    }


@router.delete("/current", status_code=status.HTTP_200_OK)
def delete_current_session(
    response: Response,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """End the current anonymous session and clear the session cookie."""
    SessionService.end_session(db, current_session.id)
    response.delete_cookie("session_token")
    return {"message": "Session successfully ended.", "status": "completed"}
