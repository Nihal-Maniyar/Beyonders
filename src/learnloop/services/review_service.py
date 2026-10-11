"""Review service for scheduling and querying revision tasks (P2)."""

from typing import List, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import ReviewTaskModel
from learnloop.repositories.review_tasks import ReviewTaskRepository


class ReviewService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ReviewTaskRepository(session)

    def schedule_misconception_review(
        self,
        learner_id: str,
        concept_id: str,
        diagnosis_code: str,
        source_attempt_id: Optional[str] = None,
    ) -> ReviewTaskModel:
        reason = f"Review triggered by detected misconception {diagnosis_code}."
        return self.repo.create_task(
            learner_id=learner_id,
            concept_id=concept_id,
            reason=reason,
            due_in_days=1,
            source_attempt_id=source_attempt_id,
        )

    def get_due_tasks(self, learner_id: str) -> List[ReviewTaskModel]:
        return self.repo.get_due_tasks(learner_id)
