"""Session progress report endpoint conforming to context.md Section 22."""

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession
from learnloop.services.relational_assessment_service import RelationalAssessmentService

router = APIRouter(prefix="/progress", tags=["progress"])


class AssessmentScoreSummary(BaseModel):
    completed: bool
    raw_score: Optional[float] = None
    max_score: Optional[float] = None
    percent: Optional[float] = None


class ComparisonSummary(BaseModel):
    is_comparable: bool
    percentage_point_change: Optional[float] = None
    status_message: str


class MisconceptionItem(BaseModel):
    code: str
    description: str
    confidence: Optional[float] = None
    status: str


class ProgressResponse(BaseModel):
    pre_assessment: AssessmentScoreSummary
    post_assessment: AssessmentScoreSummary
    comparison: ComparisonSummary
    misconceptions: List[MisconceptionItem]


@router.get("", response_model=ProgressResponse)
def get_session_progress_report(
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve derived progress report comparing pre/post outcomes for the active session."""
    return RelationalAssessmentService.get_progress(db, current_session.id)
