"""Assessment repository."""

import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import AssessmentResponseModel, AssessmentRunModel


class AssessmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_run(
        self,
        learner_id: str,
        phase: str,  # pre, post
        assessment_version: str = "fractions-v1.0",
        session_id: Optional[str] = None,
    ) -> AssessmentRunModel:
        run = AssessmentRunModel(
            learner_id=learner_id,
            session_id=session_id,
            phase=phase,
            assessment_version=assessment_version,
        )
        self.session.add(run)
        self.session.flush()
        return run

    def record_response(
        self,
        run_id: str,
        question_id: str,
        concept_id: str,
        answer_text: str,
        is_correct: bool,
    ) -> AssessmentResponseModel:
        # Check if already answered to prevent accidental duplicates
        existing = (
            self.session.query(AssessmentResponseModel)
            .filter(
                AssessmentResponseModel.assessment_run_id == run_id,
                AssessmentResponseModel.question_id == question_id,
            )
            .first()
        )
        if existing:
            existing.answer_text = answer_text
            existing.is_correct = is_correct
            self.session.flush()
            return existing

        resp = AssessmentResponseModel(
            assessment_run_id=run_id,
            question_id=question_id,
            concept_id=concept_id,
            answer_text=answer_text,
            is_correct=is_correct,
        )
        self.session.add(resp)
        self.session.flush()
        return resp

    def complete_run(self, run_id: str) -> Optional[AssessmentRunModel]:
        run = self.session.query(AssessmentRunModel).filter(AssessmentRunModel.id == run_id).first()
        if run:
            run.completed_at = datetime.datetime.now(datetime.timezone.utc)
            self.session.flush()
        return run

    def get_run(self, run_id: str) -> Optional[AssessmentRunModel]:
        return (
            self.session.query(AssessmentRunModel).filter(AssessmentRunModel.id == run_id).first()
        )

    def get_run_responses(self, run_id: str) -> List[AssessmentResponseModel]:
        return (
            self.session.query(AssessmentResponseModel)
            .filter(AssessmentResponseModel.assessment_run_id == run_id)
            .order_by(AssessmentResponseModel.answered_at.asc())
            .all()
        )

    def get_latest_completed_run(self, learner_id: str, phase: str) -> Optional[AssessmentRunModel]:
        return (
            self.session.query(AssessmentRunModel)
            .filter(
                AssessmentRunModel.learner_id == learner_id,
                AssessmentRunModel.phase == phase,
                AssessmentRunModel.completed_at.isnot(None),
            )
            .order_by(AssessmentRunModel.completed_at.desc())
            .first()
        )
