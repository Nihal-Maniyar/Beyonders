"""FastAPI dependencies for database access and anonymous session authentication."""

from typing import Generator, Optional

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from learnloop.db.models import LearningSession
from learnloop.db.session import get_db_session
from learnloop.services.session_service import SessionService


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session per request."""
    with get_db_session() as session:
        yield session


def get_current_session(
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> LearningSession:
    """Validate anonymous session token from Authorization header, X-Session-Token header, or cookie."""
    raw_token = None

    if authorization and authorization.lower().startswith("bearer "):
        raw_token = authorization[7:].strip()
    elif x_session_token:
        raw_token = x_session_token.strip()
    elif session_token:
        raw_token = session_token.strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "MISSING_SESSION_TOKEN",
                    "message": "Anonymous session token is required to access this resource.",
                    "details": [],
                }
            },
        )

    session_obj = SessionService.get_by_token(db, raw_token)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_OR_EXPIRED_SESSION",
                    "message": "The session token is invalid, revoked, or has expired.",
                    "details": [],
                }
            },
        )

    return session_obj
