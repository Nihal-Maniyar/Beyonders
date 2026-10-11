"""Assessment service orchestrating pre/post assessment runs and reporting."""

from typing import Optional

from sqlalchemy.orm import Session

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.domain.assessment_rules import (
    AssessmentResponseItem,
    generate_pre_post_report,
)
from learnloop.domain.diagnosis_rules import is_answer_correct
from learnloop.repositories.assessments import AssessmentRepository
from learnloop.schemas.assessment import PrePostReport


class AssessmentService:
    def __init__(self, session: Session, content_bank: Optional[ContentBank] = None):
        self.session = session
        self.bank = content_bank or get_content_bank()
        self.repo = AssessmentRepository(session)

    def start_pre_assessment(self, learner_id: str, session_id: Optional[str] = None):
        return self.repo.create_run(learner_id=learner_id, phase="pre", session_id=session_id)

    def start_post_assessment(self, learner_id: str, session_id: Optional[str] = None):
        return self.repo.create_run(learner_id=learner_id, phase="post", session_id=session_id)

    def record_answer(self, run_id: str, question_id: str, student_answer: str):
        question = self.bank.get_question(question_id)
        if not question:
            raise ValueError(f"Unknown question_id: {question_id}")

        correct = is_answer_correct(
            student_answer, question.correct_answer, question.accepted_answers
        )
        return self.repo.record_response(
            run_id=run_id,
            question_id=question_id,
            concept_id=question.concept_id,
            answer_text=student_answer,
            is_correct=correct,
        )

    def complete_run(self, run_id: str):
        return self.repo.complete_run(run_id)

    def get_pre_post_report(self, learner_id: str) -> Optional[PrePostReport]:
        pre_run = self.repo.get_latest_completed_run(learner_id, phase="pre")
        post_run = self.repo.get_latest_completed_run(learner_id, phase="post")

        if not pre_run or not post_run:
            return None

        pre_responses = [
            AssessmentResponseItem(
                question_id=r.question_id,
                concept_id=r.concept_id,
                is_correct=r.is_correct,
            )
            for r in self.repo.get_run_responses(pre_run.id)
        ]

        post_responses = [
            AssessmentResponseItem(
                question_id=r.question_id,
                concept_id=r.concept_id,
                is_correct=r.is_correct,
            )
            for r in self.repo.get_run_responses(post_run.id)
        ]

        return generate_pre_post_report(
            learner_id=learner_id,
            pre_responses=pre_responses,
            post_responses=post_responses,
            assessment_version=pre_run.assessment_version,
        )
