"""Database engine, session factory, and initialization utilities."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from learnloop.config import settings
from learnloop.db.base import Base


def create_app_engine(database_url: str = None):
    url = database_url or settings.database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args, echo=False)


engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(target_engine=None) -> None:
    """Initialize database tables idempotently."""
    e = target_engine or engine
    Base.metadata.create_all(bind=e)


@contextmanager
def get_db_session(session_factory=None) -> Generator[Session, None, None]:
    """Provide a transactional database session."""
    factory = session_factory or SessionLocal
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
