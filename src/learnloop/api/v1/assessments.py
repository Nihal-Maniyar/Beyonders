"""Assessments and attempts API endpoints conforming to context.md Section 22."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession
from learnloop.services.relational_assessment_service import RelationalAssessmentService

router = APIRouter(tags=["assessments"])


# --- Pydantic Request / Response Schemas ---


class OptionResponse(BaseModel):
    id: str
    option_key: str
    option_text: str


class QuestionResponse(BaseModel):
    id: str
    code: str
    position: int
    prompt: str
    question_type: str
    points_possible: float
    options: List[OptionResponse]


class AssessmentSafeResponse(BaseModel):
    id: str
    code: str
    title: str
    assessment_type: str
    version: int
    questions: List[QuestionResponse]


class AttemptStartResponse(BaseModel):
    id: str
    assessment_id: str
    attempt_no: int
    status: str


class AnswerSubmissionRequest(BaseModel):
    question_id: str
    selected_option_id: Optional[str] = None
    answer_text: Optional[str] = None


class AnswerSubmissionResponse(BaseModel):
    id: str
    attempt_id: str
    question_id: str
    selected_option_id: Optional[str] = None
    is_correct: Optional[bool] = None
    points_awarded: Optional[float] = None


class AttemptDetailResponse(BaseModel):
    id: str
    assessment_id: str
    attempt_no: int
    status: str
    raw_score: Optional[float] = None
    max_score: Optional[float] = None
    answers_count: int


# --- Endpoints ---


@router.get("/assessments/{code}", response_model=AssessmentSafeResponse)
def get_assessment_definition(
    code: str,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve safe assessment definition with ordered questions and choices.

    Guarantees internal answer keys and correctness flags are never exposed.
    """
    definition = RelationalAssessmentService.get_safe_assessment(db, code)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": f"Assessment '{code}' is not available or inactive.",
                    "details": [],
                }
            },
        )
    return definition


@router.post(
    "/assessments/{code}/attempts",
    response_model=AttemptStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_assessment_attempt(
    code: str,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Start a new assessment attempt for the active anonymous session."""
    try:
        attempt = RelationalAssessmentService.start_attempt(
            db, session_id=current_session.id, assessment_code=code
        )
        return {
            "id": attempt.id,
            "assessment_id": attempt.assessment_id,
            "attempt_no": attempt.attempt_no,
            "status": attempt.status,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e), "details": []}},
        )


@router.get("/attempts/{attempt_id}", response_model=AttemptDetailResponse)
def get_attempt_detail(
    attempt_id: str,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Fetch status and answered progress of an attempt, enforcing session ownership."""
    attempt = RelationalAssessmentService.get_attempt(
        db, attempt_id=attempt_id, session_id=current_session.id
    )
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "ATTEMPT_NOT_FOUND",
                    "message": "Attempt not found or belongs to a different session.",
                    "details": [],
                }
            },
        )
    return {
        "id": attempt.id,
        "assessment_id": attempt.assessment_id,
        "attempt_no": attempt.attempt_no,
        "status": attempt.status,
        "raw_score": attempt.raw_score,
        "max_score": attempt.max_score,
        "answers_count": len(attempt.answers),
    }


@router.post(
    "/attempts/{attempt_id}/answers",
    response_model=AnswerSubmissionResponse,
    status_code=status.HTTP_200_OK,
)
def submit_answer_to_attempt(
    attempt_id: str,
    payload: AnswerSubmissionRequest,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Submit an answer for a question within an active attempt.

    Scores server-side and validates option and question membership.
    """
    try:
        sub = RelationalAssessmentService.submit_answer(
            db=db,
            attempt_id=attempt_id,
            session_id=current_session.id,
            question_id=payload.question_id,
            selected_option_id=payload.selected_option_id,
            answer_text=payload.answer_text,
        )
        return {
            "id": sub.id,
            "attempt_id": sub.attempt_id,
            "question_id": sub.question_id,
            "selected_option_id": sub.selected_option_id,
            "is_correct": sub.is_correct,
            "points_awarded": sub.points_awarded,
        }
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Attempt belongs to a different session.",
                    "details": [],
                }
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_SUBMISSION",
                    "message": str(e),
                    "details": [],
                }
            },
        )


@router.post("/attempts/{attempt_id}/complete", response_model=AttemptDetailResponse)
def complete_assessment_attempt(
    attempt_id: str,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Complete an assessment attempt and finalize score transactionally.

    Idempotent: repeating the call will not inflate score or change completion status.
    """
    try:
        attempt = RelationalAssessmentService.complete_attempt(
            db, attempt_id=attempt_id, session_id=current_session.id
        )
        return {
            "id": attempt.id,
            "assessment_id": attempt.assessment_id,
            "attempt_no": attempt.attempt_no,
            "status": attempt.status,
            "raw_score": attempt.raw_score,
            "max_score": attempt.max_score,
            "answers_count": len(attempt.answers),
        }
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Attempt belongs to a different session.",
                    "details": [],
                }
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "COMPLETION_ERROR",
                    "message": str(e),
                    "details": [],
                }
            },
        )
