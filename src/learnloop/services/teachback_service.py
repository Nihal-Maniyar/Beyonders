"""TeachBack service orchestrating rubric evaluation and persistence."""

import json
from typing import Optional

from sqlalchemy.orm import Session

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.db.models import TeachBackEvaluationModel, TeachBackSubmissionModel
from learnloop.domain.teachback_rules import evaluate_teachback_text
from learnloop.schemas.teachback import TeachBackEvaluation


class TeachBackService:
    def __init__(self, session: Session, content_bank: Optional[ContentBank] = None):
        self.session = session
        self.bank = content_bank or get_content_bank()

    def submit_and_evaluate(
        self,
        learner_id: str,
        explanation: str,
        input_source: str = "typed",
        session_id: Optional[str] = None,
    ) -> TeachBackEvaluation:
        """Evaluate explanation against rubric and persist submission + evaluation."""
        eval_result = evaluate_teachback_text(explanation, content_bank=self.bank)

        # Persist submission
        sub = TeachBackSubmissionModel(
            learner_id=learner_id,
            session_id=session_id,
            content_version=eval_result.content_version,
            response_text=explanation,
            input_source=input_source,
        )
        self.session.add(sub)
        self.session.flush()

        # Persist evaluation
        eval_record = TeachBackEvaluationModel(
            submission_id=sub.id,
            rubric_version=eval_result.rubric_id,
            criterion_results_json=json.dumps(
                [r.model_dump() for r in eval_result.criterion_results]
            ),
            earned_points=eval_result.earned_points,
            possible_points=eval_result.possible_points,
            coverage_percent=eval_result.coverage_percent,
            overall_feedback=eval_result.overall_feedback,
            recommended_concepts_json=json.dumps(eval_result.recommended_concepts),
        )
        self.session.add(eval_record)
        self.session.flush()

        return eval_result
