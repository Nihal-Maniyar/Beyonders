"""API endpoints for Socratic tutoring, practice diagnostics, and teach-back evaluation.

Implements:
- POST /api/v1/answers/{answer_id}/reasoning
- POST /api/v1/tutoring/practice/diagnose (alias POST /api/v1/tutor/messages)
- POST /api/v1/tutoring/teach-back/evaluate (alias POST /api/v1/tutor/teach-back)
- GET  /api/v1/tutoring/history (alias GET /api/v1/tutor/history)
- GET  /api/v1/tutoring/misconceptions (alias GET /api/v1/tutor/misconceptions)
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from learnloop.api.v1.deps import get_current_session, get_db
from learnloop.db.models import LearningSession
from learnloop.services.tutoring_service import TutoringService

router = APIRouter(tags=["Tutoring & Diagnostics"])


# --- Schemas ---


class ReasoningSubmissionRequest(BaseModel):
    response_text: str = Field(..., min_length=1, description="Student reasoning explanation")
    input_mode: str = Field("text", description="text or speech_transcript")


class PracticeDiagnoseRequest(BaseModel):
    question_code: Optional[str] = None
    question_id: Optional[str] = None
    student_answer: Optional[str] = None
    reasoning_text: Optional[str] = None
    # Support Socratic tutor message format
    message: Optional[str] = None
    input_mode: str = "text"


class TeachBackEvaluateRequest(BaseModel):
    explanation: str = Field(
        ..., min_length=1, description="Student conceptual explanation for teach-back"
    )
    input_mode: str = "text"


# --- Endpoints ---


@router.post("/answers/{answer_id}/reasoning", status_code=status.HTTP_201_CREATED)
def submit_answer_reasoning(
    answer_id: str,
    payload: ReasoningSubmissionRequest,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Record an explanation / reasoning response for a previously submitted answer."""
    try:
        result = TutoringService.record_reasoning(
            db=db,
            session_id=current_session.id,
            answer_submission_id=answer_id,
            response_text=payload.response_text,
            input_mode=payload.input_mode,
        )
        db.commit()
        return result
    except PermissionError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Answer submission does not belong to the active session.",
                    "details": [],
                }
            },
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "ANSWER_NOT_FOUND",
                    "message": str(e),
                    "details": [],
                }
            },
        )


@router.post("/tutoring/practice/diagnose", status_code=status.HTTP_200_OK)
@router.post("/tutor/messages", status_code=status.HTTP_200_OK)
def diagnose_practice_answer(
    payload: PracticeDiagnoseRequest,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Diagnose a student's practice question answer and reasoning deterministically.

    Identifies misconceptions (M1-M4, S1, U1), logs hypothesis and dialogue,
    and returns Socratic guidance and remediation activity.
    """
    question_identifier = payload.question_code or payload.question_id
    if not question_identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Must provide either question_code or question_id.",
                    "details": [],
                }
            },
        )

    student_answer = payload.student_answer or payload.message
    if not student_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Must provide student_answer or message.",
                    "details": [],
                }
            },
        )

    try:
        result = TutoringService.diagnose_practice(
            db=db,
            session_id=current_session.id,
            question_identifier=question_identifier,
            student_answer=student_answer,
            reasoning_text=payload.reasoning_text,
            input_mode=payload.input_mode,
        )
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "QUESTION_NOT_FOUND",
                    "message": str(e),
                    "details": [],
                }
            },
        )
    except PermissionError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED_SESSION",
                    "message": str(e),
                    "details": [],
                }
            },
        )


@router.post("/tutoring/teach-back/evaluate", status_code=status.HTTP_200_OK)
@router.post("/tutor/teach-back", status_code=status.HTTP_200_OK)
def evaluate_teach_back_explanation(
    payload: TeachBackEvaluateRequest,
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Evaluate a learner's teach-back explanation using the 5-point rubric (R1-R5)."""
    try:
        evaluation = TutoringService.evaluate_teachback(
            db=db,
            session_id=current_session.id,
            explanation=payload.explanation,
            input_mode=payload.input_mode,
        )
        db.commit()
        return evaluation
    except PermissionError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED_SESSION",
                    "message": str(e),
                    "details": [],
                }
            },
        )


@router.get("/tutoring/history", response_model=List[Dict[str, Any]])
@router.get("/tutor/history", response_model=List[Dict[str, Any]])
def get_tutoring_interaction_history(
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve ordered tutoring dialogue history for the authenticated session."""
    return TutoringService.get_history(db=db, session_id=current_session.id)


@router.get("/tutoring/misconceptions", response_model=List[Dict[str, Any]])
@router.get("/tutor/misconceptions", response_model=List[Dict[str, Any]])
def get_session_misconceptions(
    current_session: LearningSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Retrieve active misconception hypotheses for the authenticated session."""
    return TutoringService.get_misconceptions(db=db, session_id=current_session.id)
