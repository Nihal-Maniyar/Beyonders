"""Learner repository."""

from typing import Optional

from sqlalchemy.orm import Session

from learnloop.db.models import LearnerModel, LearningSessionModel


class LearnerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, learner_id: str) -> Optional[LearnerModel]:
        return self.session.query(LearnerModel).filter(LearnerModel.id == learner_id).first()

    def get_or_create(
        self, learner_id: str, display_name: Optional[str] = None, is_demo: bool = True
    ) -> LearnerModel:
        learner = self.get_by_id(learner_id)
        if not learner:
            learner = LearnerModel(
                id=learner_id,
                display_name=display_name or f"Learner-{learner_id[:6]}",
                is_demo=is_demo,
            )
            self.session.add(learner)
            self.session.flush()
        return learner

    def create_learning_session(
        self,
        learner_id: str,
        chapter_id: str = "CH_FRACTIONS_01",
        content_version: str = "fractions-v1.0",
    ) -> LearningSessionModel:
        session_obj = LearningSessionModel(
            learner_id=learner_id,
            chapter_id=chapter_id,
            content_version=content_version,
            current_stage="WELCOME",
        )
        self.session.add(session_obj)
        self.session.flush()
        return session_obj
