"""Diagnosis service orchestrating misconception identification and attempt persistence."""

from typing import Optional

from sqlalchemy.orm import Session

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.domain.diagnosis_rules import classify_reasoning
from learnloop.repositories.attempts import AttemptRepository
from learnloop.schemas.diagnosis import DiagnosisResult
from learnloop.services.mastery_service import MasteryService


class DiagnosisService:
    def __init__(self, session: Session, content_bank: Optional[ContentBank] = None):
        self.session = session
        self.bank = content_bank or get_content_bank()
        self.attempt_repo = AttemptRepository(session)
        self.mastery_service = MasteryService(session, self.bank)

    def diagnose_and_record(
        self,
        learner_id: str,
        question_id: str,
        student_answer: str,
        reasoning_text: Optional[str] = None,
        source: str = "typed",
        session_id: Optional[str] = None,
        follow_up_to_attempt_id: Optional[str] = None,
    ) -> DiagnosisResult:
        """Run deterministic diagnosis, persist the attempt, and recompute mastery."""
        question = self.bank.get_question(question_id)
        if not question:
            raise ValueError(f"Unknown question_id: {question_id}")

        result: DiagnosisResult = classify_reasoning(
            question_id=question_id,
            student_answer=student_answer,
            reasoning_text=reasoning_text,
            content_bank=self.bank,
        )

        # Persist attempt record
        self.attempt_repo.record_attempt(
            learner_id=learner_id,
            question_id=question_id,
            concept_id=question.concept_id,
            content_version=question.content_version,
            response_text=student_answer,
            reasoning_text=reasoning_text,
            is_correct=result.is_correct,
            reasoning_status=result.reasoning_status.value,
            diagnosis_code=result.diagnosis_code.value if result.diagnosis_code else None,
            diagnosis_certainty=result.certainty.value if result.certainty else None,
            diagnosis_evidence=result.evidence,
            clarification_required=result.clarification_required,
            activity_id=result.next_activity_id,
            session_id=session_id,
            source=source,
            follow_up_to_attempt_id=follow_up_to_attempt_id,
        )

        # Recalculate concept mastery from updated attempts
        self.mastery_service.recompute_learner_mastery(learner_id, question.concept_id)

        return result
