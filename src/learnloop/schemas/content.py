"""Pydantic schemas for content validation."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class WorkedExample(BaseModel):
    example_id: str
    prompt: str
    steps: List[str]


class Concept(BaseModel):
    concept_id: str
    title: str
    learning_objectives: List[str]
    prerequisites: List[str] = Field(default_factory=list)
    verified_explanation: str
    intuitive_analogy: str
    worked_examples: List[WorkedExample] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    question_ids: List[str] = Field(default_factory=list)
    misconception_ids: List[str] = Field(default_factory=list)


class Chapter(BaseModel):
    chapter_id: str
    title: str
    subject: str
    grade_level: str
    content_version: str
    reviewed_by: str
    reviewed_at: str
    learning_objectives: List[str]
    concepts: List[Concept]


class Question(BaseModel):
    question_id: str
    concept_id: str
    content_version: str
    question_text: str
    question_type: str = "multiple_choice"
    difficulty: str = "medium"
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    accepted_answers: List[str] = Field(default_factory=list)
    verified_explanation: str
    learning_objective: str
    is_transfer_question: bool = False
    misconception_mappings: Dict[str, str] = Field(default_factory=dict)
    remediation_activity_ids: List[str] = Field(default_factory=list)


class RemediationActivity(BaseModel):
    activity_id: str
    concept_id: str
    title: str
    purpose: str
    instructions: str
    visual_representation: Optional[str] = None
    target_diagnosis_codes: List[str] = Field(default_factory=list)
    question_ids: List[str] = Field(default_factory=list)
    expected_learning_evidence: str


class RubricCriterion(BaseModel):
    criterion_id: str
    concept_id: str
    title: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    levels: Dict[str, str]


class Rubric(BaseModel):
    rubric_id: str
    title: str
    content_version: str
    criteria: List[RubricCriterion]
