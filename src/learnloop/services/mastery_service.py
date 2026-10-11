"""Mastery service orchestrating pure calculations and persistent caching."""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.domain.mastery_rules import (
    AttemptRecord,
    ConceptMasterySummary,
    calculate_concept_mastery,
)
from learnloop.repositories.attempts import AttemptRepository
from learnloop.repositories.mastery import MasteryRepository
from learnloop.schemas.diagnosis import ReasoningStatus


class MasteryService:
    def __init__(self, session: Session, content_bank: Optional[ContentBank] = None):
        self.session = session
        self.bank = content_bank or get_content_bank()
        self.attempt_repo = AttemptRepository(session)
        self.mastery_repo = MasteryRepository(session)

    def recompute_learner_mastery(
        self,
        learner_id: str,
        concept_id: Optional[str] = None,
    ) -> Dict[str, ConceptMasterySummary]:
        """Recalculate mastery from attempt history and update database cache."""
        target_concepts = (
            [concept_id] if concept_id else [c.concept_id for c in self.bank.chapter.concepts]
        )
        attempts = self.attempt_repo.get_learner_attempts(learner_id)

        # Convert to AttemptRecord domain items
        domain_attempts: List[AttemptRecord] = []
        for a in attempts:
            q = self.bank.get_question(a.question_id)
            is_transfer = q.is_transfer_question if q else False
            domain_attempts.append(
                AttemptRecord(
                    attempt_id=a.id,
                    concept_id=a.concept_id,
                    question_id=a.question_id,
                    is_correct=a.is_correct,
                    reasoning_status=ReasoningStatus(a.reasoning_status)
                    if a.reasoning_status in ReasoningStatus._value2member_map_
                    else ReasoningStatus.NOT_ASSESSED,
                    is_transfer_question=is_transfer,
                    created_at=a.created_at.isoformat() if a.created_at else None,
                )
            )

        summaries: Dict[str, ConceptMasterySummary] = {}
        for cid in target_concepts:
            summary = calculate_concept_mastery(cid, domain_attempts)
            self.mastery_repo.upsert_mastery(learner_id, summary)
            summaries[cid] = summary

        return summaries

    def get_learner_masteries(self, learner_id: str) -> Dict[str, ConceptMasterySummary]:
        """Get cached or recomputed masteries for learner."""
        db_records = self.mastery_repo.get_learner_masteries(learner_id)
        if not db_records:
            return self.recompute_learner_mastery(learner_id)

        summaries = {}
        for cid, rec in db_records.items():
            from learnloop.domain.mastery_rules import MasteryStatus

            summaries[cid] = ConceptMasterySummary(
                concept_id=cid,
                status=MasteryStatus(rec.status),
                score=rec.score,
                evidence_attempt_count=rec.evidence_attempt_count,
                distinct_question_count=rec.distinct_question_count,
                transfer_passed=rec.transfer_passed,
                last_evidence_at=rec.last_evidence_at.isoformat() if rec.last_evidence_at else None,
                policy_version=rec.policy_version,
            )
        return summaries
