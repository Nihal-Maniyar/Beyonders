"""Schemas for teach-back evaluation."""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class CriterionStatus(str, Enum):
    DEMONSTRATED = "demonstrated"
    PARTIAL = "partial"
    INCORRECT = "incorrect"
    NOT_DEMONSTRATED = "not_demonstrated"


class CriterionResult(BaseModel):
    criterion_id: str
    status: CriterionStatus
    evidence: str


class TeachBackEvaluation(BaseModel):
    rubric_id: str = "RUBRIC_FRACTIONS_01"
    content_version: str = "fractions-v1.0"
    criterion_results: List[CriterionResult]
    earned_points: float
    possible_points: float = 5.0
    coverage_percent: float
    overall_feedback: str
    recommended_concepts: List[str] = Field(default_factory=list)
    clarification_required: bool = False
