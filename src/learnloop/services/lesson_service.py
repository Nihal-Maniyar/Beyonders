"""Lesson service for querying instructional fraction content."""

from typing import List, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import Lesson


class LessonService:
    @staticmethod
    def list_lessons(db: Session) -> List[Lesson]:
        """Fetch all published lessons ordered by sequence_no."""
        return (
            db.query(Lesson)
            .filter(Lesson.status == "published")
            .order_by(Lesson.sequence_no.asc())
            .all()
        )

    @staticmethod
    def get_lesson(db: Session, lesson_identifier: str) -> Optional[Lesson]:
        """Fetch a lesson by UUID id or code."""
        return (
            db.query(Lesson)
            .filter((Lesson.id == lesson_identifier) | (Lesson.code == lesson_identifier))
            .first()
        )
