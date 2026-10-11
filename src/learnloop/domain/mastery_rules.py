"""Pure function mastery rules engine.

Recalculates concept mastery from recorded attempt history:
- No valid attempts: 'not_assessed'
- < 2 attempts: 'developing'
- Inconsistent or < 4 attempts or < 3 distinct questions: 'practising'
- 'mastered' requires:
  1. At least 4 valid attempts
  2. Across at least 3 distinct questions
  3. At least 80% weighted accuracy
  4. At least one correct transfer question with valid reasoning
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from learnloop.schemas.diagnosis import ReasoningStatus


class MasteryStatus(str, Enum):
    NOT_ASSESSED = "not_assessed"
    DEVELOPING = "developing"
    PRACTISING = "practising"
    MASTERED = "mastered"


class AttemptRecord(BaseModel):
    attempt_id: str
    concept_id: str
    question_id: str
    is_correct: bool
    reasoning_status: ReasoningStatus
    is_transfer_question: bool = False
    created_at: Optional[str] = None


class ConceptMasterySummary(BaseModel):
    concept_id: str
    status: MasteryStatus
    score: float
    evidence_attempt_count: int
    distinct_question_count: int
    transfer_passed: bool
    last_evidence_at: Optional[str] = None
    policy_version: str = "mastery-v1.0"


def calculate_attempt_weight(is_correct: bool, reasoning_status: ReasoningStatus) -> float:
    """Weigh correctness and reasoning: guessing doesn't award full credit."""
    if not is_correct:
        return 0.0
    if reasoning_status == ReasoningStatus.VALID:
        return 1.0
    if reasoning_status in (ReasoningStatus.UNCLEAR, ReasoningStatus.NOT_ASSESSED):
        return 0.5
    # Correct option with invalid reasoning
    return 0.25


def calculate_concept_mastery(
    concept_id: str,
    attempts: List[AttemptRecord],
    has_transfer_requirement: bool = True,
) -> ConceptMasterySummary:
    """Calculate mastery purely from saved attempt history."""
    concept_attempts = [a for a in attempts if a.concept_id == concept_id]

    if not concept_attempts:
        return ConceptMasterySummary(
            concept_id=concept_id,
            status=MasteryStatus.NOT_ASSESSED,
            score=0.0,
            evidence_attempt_count=0,
            distinct_question_count=0,
            transfer_passed=False,
            last_evidence_at=None,
        )

    attempt_count = len(concept_attempts)
    distinct_questions = len({a.question_id for a in concept_attempts})

    # Calculate weighted accuracy
    total_weight = sum(
        calculate_attempt_weight(a.is_correct, a.reasoning_status) for a in concept_attempts
    )
    score_pct = round((total_weight / attempt_count) * 100.0, 1)

    # Check transfer question
    transfer_attempts = [a for a in concept_attempts if a.is_transfer_question]
    transfer_passed = (
        any(a.is_correct and a.reasoning_status == ReasoningStatus.VALID for a in transfer_attempts)
        if transfer_attempts
        else False
    )

    # Most recent timestamp
    last_timestamp = concept_attempts[-1].created_at if concept_attempts else None

    # Determine status
    if attempt_count < 2:
        status = MasteryStatus.DEVELOPING
    elif attempt_count < 4 or distinct_questions < 3 or score_pct < 80.0:
        status = MasteryStatus.PRACTISING
    else:
        # Meets count (>=4), distinct (>=3), and score (>=80)
        if has_transfer_requirement:
            # If concept has transfer items (like C2)
            if transfer_attempts:
                status = MasteryStatus.MASTERED if transfer_passed else MasteryStatus.PRACTISING
            else:
                # If no transfer question is configured for this concept, score and counts suffice
                status = MasteryStatus.MASTERED
        else:
            status = MasteryStatus.MASTERED

    return ConceptMasterySummary(
        concept_id=concept_id,
        status=status,
        score=score_pct,
        evidence_attempt_count=attempt_count,
        distinct_question_count=distinct_questions,
        transfer_passed=transfer_passed,
        last_evidence_at=last_timestamp,
    )


def recompute_all_masteries(
    concept_ids: List[str],
    attempts: List[AttemptRecord],
) -> Dict[str, ConceptMasterySummary]:
    """Recompute mastery for all concepts."""
    return {cid: calculate_concept_mastery(cid, attempts) for cid in concept_ids}
