"""Attempt repository."""

from typing import List, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import AttemptModel


class AttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def record_attempt(
        self,
        learner_id: str,
        question_id: str,
        concept_id: str,
        response_text: str,
        is_correct: bool,
        content_version: str = "fractions-v1.0",
        reasoning_text: Optional[str] = None,
        reasoning_status: str = "not_assessed",
        diagnosis_code: Optional[str] = None,
        diagnosis_certainty: Optional[str] = None,
        diagnosis_evidence: Optional[str] = None,
        clarification_required: bool = False,
        activity_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source: str = "typed",
        follow_up_to_attempt_id: Optional[str] = None,
    ) -> AttemptModel:
        attempt = AttemptModel(
            learner_id=learner_id,
            session_id=session_id,
            question_id=question_id,
            concept_id=concept_id,
            content_version=content_version,
            response_text=response_text,
            reasoning_text=reasoning_text,
            is_correct=is_correct,
            reasoning_status=reasoning_status,
            diagnosis_code=diagnosis_code,
            diagnosis_certainty=diagnosis_certainty,
            diagnosis_evidence=diagnosis_evidence,
            clarification_required=clarification_required,
            activity_id=activity_id,
            source=source,
            follow_up_to_attempt_id=follow_up_to_attempt_id,
        )
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def get_learner_attempts(
        self,
        learner_id: str,
        concept_id: Optional[str] = None,
    ) -> List[AttemptModel]:
        query = self.session.query(AttemptModel).filter(AttemptModel.learner_id == learner_id)
        if concept_id:
            query = query.filter(AttemptModel.concept_id == concept_id)
        return query.order_by(AttemptModel.created_at.asc()).all()
