"""Mastery repository."""

import datetime
from typing import Dict

from sqlalchemy.orm import Session

from learnloop.db.models import ConceptMasteryModel
from learnloop.domain.mastery_rules import ConceptMasterySummary


class MasteryRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_mastery(
        self, learner_id: str, summary: ConceptMasterySummary
    ) -> ConceptMasteryModel:
        record = (
            self.session.query(ConceptMasteryModel)
            .filter(
                ConceptMasteryModel.learner_id == learner_id,
                ConceptMasteryModel.concept_id == summary.concept_id,
            )
            .first()
        )
        if not record:
            record = ConceptMasteryModel(
                learner_id=learner_id,
                concept_id=summary.concept_id,
            )
            self.session.add(record)

        record.status = summary.status.value
        record.score = summary.score
        record.evidence_attempt_count = summary.evidence_attempt_count
        record.distinct_question_count = summary.distinct_question_count
        record.transfer_passed = summary.transfer_passed
        record.policy_version = summary.policy_version
        record.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.flush()
        return record

    def get_learner_masteries(self, learner_id: str) -> Dict[str, ConceptMasteryModel]:
        records = (
            self.session.query(ConceptMasteryModel)
            .filter(ConceptMasteryModel.learner_id == learner_id)
            .all()
        )
        return {r.concept_id: r for r in records}
