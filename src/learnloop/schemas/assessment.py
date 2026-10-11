"""Schemas for assessment and reporting."""

from typing import Dict, List

from pydantic import BaseModel, Field


class ConceptScore(BaseModel):
    concept_id: str
    pre_correct: int
    pre_total: int
    post_correct: int
    post_total: int
    pre_percent: float
    post_percent: float
    change_pp: float


class PrePostReport(BaseModel):
    learner_id: str
    assessment_version: str = "fractions-v1.0"
    paired_sample_count: int = 1
    pre_correct: int
    pre_total: int = 6
    pre_percent: float
    post_correct: int
    post_total: int = 6
    post_percent: float
    score_change_pp: float
    concept_breakdown: Dict[str, ConceptScore] = Field(default_factory=dict)
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Reusing identical assessment items can introduce a practice effect.",
            "An uncontrolled pre/post comparison (n=1) does not scientifically establish causation.",
            "A short 6-item assessment is a diagnostic snapshot and does not measure long-term retention.",
            "Transfer across novel contexts requires broader multi-step problem sets.",
        ]
    )
