"""Session service for high-entropy anonymous session lifecycle management."""

import datetime
import hashlib
import hmac
import secrets
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from learnloop.config import settings
from learnloop.db.models import LearningSession, utc_now


class SessionService:
    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Compute HMAC-SHA256 hash of a session token using the server pepper."""
        pepper = settings.session_token_pepper.encode("utf-8")
        return hmac.new(pepper, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()

    @classmethod
    def create_session(
        cls, db: Session, expiry_hours: Optional[int] = None
    ) -> Tuple[LearningSession, str]:
        """Create a new anonymous session with high-entropy token.

        Returns:
            Tuple of (LearningSession database model, raw secret token string).
        """
        raw_token = secrets.token_urlsafe(32)
        token_hash = cls.hash_token(raw_token)
        hours = expiry_hours or settings.session_expiry_hours
        expires_at = utc_now() + datetime.timedelta(hours=hours)

        session_obj = LearningSession(
            token_hash=token_hash,
            status="active",
            expires_at=expires_at,
        )
        db.add(session_obj)
        db.flush()
        return session_obj, raw_token

    @classmethod
    def get_by_token(cls, db: Session, raw_token: str) -> Optional[LearningSession]:
        """Validate token hash and check expiration."""
        token_hash = cls.hash_token(raw_token)
        session_obj = (
            db.query(LearningSession).filter(LearningSession.token_hash == token_hash).first()
        )
        if not session_obj:
            return None

        # Check expiration
        now = utc_now()
        # Ensure expires_at has timezone info for comparison if SQLite returned naive datetime
        expires = session_obj.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=datetime.timezone.utc)

        if expires <= now:
            if session_obj.status == "active":
                session_obj.status = "expired"
                db.flush()
            return None

        if session_obj.status != "active":
            return None

        return session_obj

    @classmethod
    def end_session(cls, db: Session, session_id: str) -> bool:
        """Mark an active session as completed."""
        session_obj = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session_obj:
            return False
        session_obj.status = "completed"
        session_obj.completed_at = utc_now()
        db.flush()
        return True
