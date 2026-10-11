"""FastAPI route definitions for LearnLoop AI."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from learnloop.content.loader import get_content_bank
from learnloop.db.session import get_db_session
from learnloop.repositories.learners import LearnerRepository
from learnloop.schemas.assessment import PrePostReport
from learnloop.schemas.content import Chapter, Question, RemediationActivity
from learnloop.schemas.diagnosis import DiagnosisResult
from learnloop.schemas.teachback import TeachBackEvaluation
from learnloop.services.assessment_service import AssessmentService
from learnloop.services.diagnosis_service import DiagnosisService
from learnloop.services.mastery_service import MasteryService
from learnloop.services.review_service import ReviewService
from learnloop.services.teachback_service import TeachBackService

router = APIRouter(prefix="/api")


def get_db():
    with get_db_session() as session:
        yield session


# --- Schemas ---


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    chapter_loaded: str


class LearnerSessionRequest(BaseModel):
    learner_id: str
    display_name: Optional[str] = None


class LearnerSessionResponse(BaseModel):
    learner_id: str
    display_name: str
    session_id: str
    chapter_id: str


class StartAssessmentRequest(BaseModel):
    learner_id: str
    phase: str  # "pre" | "post"
    session_id: Optional[str] = None


class AssessmentRunResponse(BaseModel):
    run_id: str
    learner_id: str
    phase: str
    assessment_version: str


class AssessmentAnswerRequest(BaseModel):
    run_id: str
    question_id: str
    student_answer: str


class CompleteAssessmentRequest(BaseModel):
    run_id: str


class PracticeDiagnoseRequest(BaseModel):
    learner_id: str
    question_id: str
    student_answer: str
    reasoning_text: Optional[str] = None
    session_id: Optional[str] = None


class TeachBackSubmitRequest(BaseModel):
    learner_id: str
    explanation: str
    session_id: Optional[str] = None


# --- Endpoints ---


@router.get("/health", response_model=HealthResponse)
def health_check():
    bank = get_content_bank()
    return HealthResponse(chapter_loaded=bank.chapter.title)


@router.get("/chapter", response_model=Chapter)
def get_chapter():
    bank = get_content_bank()
    return bank.chapter


@router.get("/assessment/fixed", response_model=List[Question])
def get_fixed_assessment_questions():
    bank = get_content_bank()
    questions = bank.get_fixed_assessment_questions()
    # Scrub correct_answer and verified_explanation to ensure assessment integrity
    scrubbed = []
    for q in questions:
        q_copy = q.model_copy()
        q_copy.correct_answer = ""
        q_copy.verified_explanation = ""
        q_copy.misconception_mappings = {}
        scrubbed.append(q_copy)
    return scrubbed


@router.get("/questions/{question_id}", response_model=Question)
def get_question(question_id: str):
    bank = get_content_bank()
    q = bank.get_question(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.get("/activities/{activity_id}", response_model=RemediationActivity)
def get_activity(activity_id: str):
    bank = get_content_bank()
    act = bank.get_activity(activity_id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
    return act


@router.post("/learners/session", response_model=LearnerSessionResponse)
def get_or_create_learner_session(
    payload: LearnerSessionRequest,
    db: Session = Depends(get_db),
):
    learner_repo = LearnerRepository(db)
    learner = learner_repo.get_or_create(
        payload.learner_id, display_name=payload.display_name, is_demo=True
    )
    bank = get_content_bank()
    session_obj = learner_repo.create_learning_session(
        learner_id=learner.id,
        chapter_id=bank.chapter.chapter_id,
        content_version=bank.chapter.content_version,
    )
    return LearnerSessionResponse(
        learner_id=learner.id,
        display_name=learner.display_name,
        session_id=session_obj.id,
        chapter_id=bank.chapter.chapter_id,
    )


@router.post("/assessment/start", response_model=AssessmentRunResponse)
def start_assessment_run(
    payload: StartAssessmentRequest,
    db: Session = Depends(get_db),
):
    assess_service = AssessmentService(db)
    if payload.phase == "pre":
        run = assess_service.start_pre_assessment(
            learner_id=payload.learner_id, session_id=payload.session_id
        )
    else:
        run = assess_service.start_post_assessment(
            learner_id=payload.learner_id, session_id=payload.session_id
        )
    return AssessmentRunResponse(
        run_id=run.id,
        learner_id=run.learner_id,
        phase=run.phase,
        assessment_version=run.assessment_version,
    )


@router.post("/assessment/answer")
def record_assessment_answer(
    payload: AssessmentAnswerRequest,
    db: Session = Depends(get_db),
):
    assess_service = AssessmentService(db)
    try:
        resp = assess_service.record_answer(
            run_id=payload.run_id,
            question_id=payload.question_id,
            student_answer=payload.student_answer,
        )
        return {"status": "saved", "response_id": resp.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assessment/complete")
def complete_assessment_run(
    payload: CompleteAssessmentRequest,
    db: Session = Depends(get_db),
):
    assess_service = AssessmentService(db)
    run = assess_service.complete_run(payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"status": "completed", "run_id": run.id}


@router.post("/practice/diagnose", response_model=DiagnosisResult)
def diagnose_practice(
    payload: PracticeDiagnoseRequest,
    db: Session = Depends(get_db),
):
    diag_service = DiagnosisService(db)
    try:
        result = diag_service.diagnose_and_record(
            learner_id=payload.learner_id,
            question_id=payload.question_id,
            student_answer=payload.student_answer,
            reasoning_text=payload.reasoning_text,
            session_id=payload.session_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/teachback/evaluate", response_model=TeachBackEvaluation)
def evaluate_teachback(
    payload: TeachBackSubmitRequest,
    db: Session = Depends(get_db),
):
    tb_service = TeachBackService(db)
    evaluation = tb_service.submit_and_evaluate(
        learner_id=payload.learner_id,
        explanation=payload.explanation,
        session_id=payload.session_id,
    )
    return evaluation


@router.get("/reports/{learner_id}", response_model=Optional[PrePostReport])
def get_pre_post_report(
    learner_id: str,
    db: Session = Depends(get_db),
):
    assess_service = AssessmentService(db)
    report = assess_service.get_pre_post_report(learner_id)
    return report


@router.get("/mastery/{learner_id}")
def get_learner_mastery(
    learner_id: str,
    db: Session = Depends(get_db),
):
    mastery_service = MasteryService(db)
    masteries = mastery_service.get_learner_masteries(learner_id)
    return {
        cid: {
            "concept_id": m.concept_id,
            "status": m.status.value,
            "score": m.score,
            "evidence_attempt_count": m.evidence_attempt_count,
            "distinct_question_count": m.distinct_question_count,
            "transfer_passed": m.transfer_passed,
        }
        for cid, m in masteries.items()
    }


@router.get("/review/{learner_id}")
def get_due_reviews(
    learner_id: str,
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)
    tasks = review_service.get_due_tasks(learner_id)
    return [
        {
            "id": t.id,
            "learner_id": t.learner_id,
            "concept_id": t.concept_id,
            "reason": t.reason,
            "due_at": t.due_at.isoformat() if t.due_at else None,
            "status": t.status,
        }
        for t in tasks
    ]
