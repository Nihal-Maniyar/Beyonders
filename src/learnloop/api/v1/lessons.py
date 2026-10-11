"""Lessons API endpoints for fraction instructional units."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession
from learnloop.services.lesson_service import LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


class ConceptRef(BaseModel):
    id: str
    code: str
    name: str


class LessonSummary(BaseModel):
    id: str
    code: str
    title: str
    sequence_no: int


class LessonDetail(BaseModel):
    id: str
    code: str
    title: str
    content: str
    sequence_no: int
    concepts: List[ConceptRef]


@router.get("", response_model=List[LessonSummary])
def list_published_lessons(
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """List all published fraction lessons in pedagogical sequence."""
    lessons = LessonService.list_lessons(db)
    return [
        {
            "id": item.id,
            "code": item.code,
            "title": item.title,
            "sequence_no": item.sequence_no,
        }
        for item in lessons
    ]


@router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson_detail(
    lesson_id: str,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve full lesson explanation and associated concepts."""
    lesson = LessonService.get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "LESSON_NOT_FOUND",
                    "message": f"Lesson '{lesson_id}' does not exist.",
                    "details": [],
                }
            },
        )

    concept_refs = [
        {"id": lc.concept.id, "code": lc.concept.code, "name": lc.concept.name}
        for lc in lesson.concepts
        if lc.concept
    ]

    return {
        "id": lesson.id,
        "code": lesson.code,
        "title": lesson.title,
        "content": lesson.content,
        "sequence_no": lesson.sequence_no,
        "concepts": concept_refs,
    }
