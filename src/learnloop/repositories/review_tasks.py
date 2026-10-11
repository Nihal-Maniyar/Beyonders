"""Review tasks repository for spaced revision queue."""

import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import ReviewTaskModel


class ReviewTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_task(
        self,
        learner_id: str,
        concept_id: str,
        reason: str,
        due_in_days: int = 1,
        source_attempt_id: Optional[str] = None,
    ) -> ReviewTaskModel:
        due_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=due_in_days)
        task = ReviewTaskModel(
            learner_id=learner_id,
            concept_id=concept_id,
            reason=reason,
            due_at=due_at,
            source_attempt_id=source_attempt_id,
            status="due",
        )
        self.session.add(task)
        self.session.flush()
        return task

    def get_due_tasks(self, learner_id: str) -> List[ReviewTaskModel]:
        return (
            self.session.query(ReviewTaskModel)
            .filter(
                ReviewTaskModel.learner_id == learner_id,
                ReviewTaskModel.status == "due",
            )
            .order_by(ReviewTaskModel.due_at.asc())
            .all()
        )

    def mark_completed(self, task_id: str) -> Optional[ReviewTaskModel]:
        task = self.session.query(ReviewTaskModel).filter(ReviewTaskModel.id == task_id).first()
        if task:
            task.status = "completed"
            task.completed_at = datetime.datetime.now(datetime.timezone.utc)
            self.session.flush()
        return task
