"""Schemas for misconception diagnosis."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DiagnosisCode(str, Enum):
    M1 = "M1"  # Whole-number bias
    M2 = "M2"  # Reversed denominator rule
    M3 = "M3"  # Numerator-only comparison
    M4 = "M4"  # Invalid equivalent-fraction transformation
    S1 = "S1"  # Arithmetic slip
    U1 = "U1"  # Insufficient evidence / uncertain
    NONE = "NONE"


class ReasoningStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNCLEAR = "unclear"
    NOT_ASSESSED = "not_assessed"


class Certainty(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class DiagnosisInput(BaseModel):
    question_id: str
    student_answer: str
    reasoning_text: Optional[str] = None
    prior_evidence: List[str] = Field(default_factory=list)
    content_version: str = "fractions-v1.0"


class DiagnosisResult(BaseModel):
    question_id: str
    is_correct: bool
    reasoning_status: ReasoningStatus
    diagnosis_code: DiagnosisCode
    certainty: Certainty
    evidence: str
    clarification_required: bool
    clarifying_question: Optional[str] = None
    next_activity_id: Optional[str] = None
    student_feedback: str  # Plain-language explanation for learner
