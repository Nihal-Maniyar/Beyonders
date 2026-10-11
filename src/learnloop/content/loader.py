"""Content loader and integrity validator for LearnLoop AI."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from learnloop.config import settings
from learnloop.schemas.content import (
    Chapter,
    Concept,
    Question,
    RemediationActivity,
    Rubric,
)

FIXED_ASSESSMENT_QUESTION_IDS = [
    "Q_C1_PRE_01",
    "Q_C1_PRE_02",
    "Q_C2_PRE_01",
    "Q_C2_PRE_02",
    "Q_C3_PRE_01",
    "Q_C3_PRE_02",
]


class ContentBank:
    """In-memory loaded and validated content bank."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.data_dir
        self.chapter: Chapter = self._load_chapter()
        self.questions: Dict[str, Question] = self._load_questions()
        self.activities: Dict[str, RemediationActivity] = self._load_activities()
        self.rubric: Rubric = self._load_rubric()
        self._validate_integrity()

    def _load_chapter(self) -> Chapter:
        path = self.data_dir / "fractions_chapter.json"
        if not path.exists():
            raise FileNotFoundError(f"Chapter file missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Chapter(**data)

    def _load_questions(self) -> Dict[str, Question]:
        path = self.data_dir / "questions.json"
        if not path.exists():
            raise FileNotFoundError(f"Questions file missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        q_dict = {}
        for q in data.get("questions", []):
            question = Question(**q)
            if question.question_id in q_dict:
                raise ValueError(f"Duplicate question_id: {question.question_id}")
            q_dict[question.question_id] = question
        return q_dict

    def _load_activities(self) -> Dict[str, RemediationActivity]:
        path = self.data_dir / "activities.json"
        if not path.exists():
            raise FileNotFoundError(f"Activities file missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        a_dict = {}
        for a in data.get("activities", []):
            activity = RemediationActivity(**a)
            if activity.activity_id in a_dict:
                raise ValueError(f"Duplicate activity_id: {activity.activity_id}")
            a_dict[activity.activity_id] = activity
        return a_dict

    def _load_rubric(self) -> Rubric:
        path = self.data_dir / "rubric.json"
        if not path.exists():
            raise FileNotFoundError(f"Rubric file missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Rubric(**data)

    def _validate_integrity(self) -> None:
        """Validate cross-references, ID sets, and fixed assessment consistency."""
        concept_ids = {c.concept_id for c in self.chapter.concepts}
        if len(concept_ids) != len(self.chapter.concepts):
            raise ValueError("Duplicate concept IDs in chapter")

        # Validate questions
        for q_id, q in self.questions.items():
            if q.concept_id not in concept_ids:
                raise ValueError(f"Question {q_id} references unknown concept {q.concept_id}")
            for a_id in q.remediation_activity_ids:
                if a_id not in self.activities:
                    raise ValueError(f"Question {q_id} references unknown activity {a_id}")
            if not q.correct_answer:
                raise ValueError(f"Question {q_id} has empty correct_answer")

        # Validate fixed assessment questions
        for fixed_id in FIXED_ASSESSMENT_QUESTION_IDS:
            if fixed_id not in self.questions:
                raise ValueError(f"Fixed assessment item {fixed_id} not found in questions bank")

        # Verify exactly 2 pre questions per concept for C1, C2, C3
        fixed_c1 = [
            q for q in FIXED_ASSESSMENT_QUESTION_IDS if self.questions[q].concept_id == "C1"
        ]
        fixed_c2 = [
            q for q in FIXED_ASSESSMENT_QUESTION_IDS if self.questions[q].concept_id == "C2"
        ]
        fixed_c3 = [
            q for q in FIXED_ASSESSMENT_QUESTION_IDS if self.questions[q].concept_id == "C3"
        ]
        if len(fixed_c1) != 2 or len(fixed_c2) != 2 or len(fixed_c3) != 2:
            raise ValueError("Fixed assessment must have exactly 2 questions each for C1, C2, C3")

        # Validate activities
        for a_id, a in self.activities.items():
            if a.concept_id not in concept_ids:
                raise ValueError(f"Activity {a_id} references unknown concept {a.concept_id}")

        # Validate rubric
        criterion_ids = set()
        for criterion in self.rubric.criteria:
            if criterion.criterion_id in criterion_ids:
                raise ValueError(f"Duplicate rubric criterion {criterion.criterion_id}")
            criterion_ids.add(criterion.criterion_id)
            if criterion.concept_id not in concept_ids:
                raise ValueError(
                    f"Criterion {criterion.criterion_id} references unknown concept {criterion.concept_id}"
                )

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        for c in self.chapter.concepts:
            if c.concept_id == concept_id:
                return c
        return None

    def get_question(self, question_id: str) -> Optional[Question]:
        return self.questions.get(question_id)

    def get_activity(self, activity_id: str) -> Optional[RemediationActivity]:
        return self.activities.get(activity_id)

    def get_fixed_assessment_questions(self) -> List[Question]:
        return [self.questions[qid] for qid in FIXED_ASSESSMENT_QUESTION_IDS]


_content_bank_instance: Optional[ContentBank] = None


def get_content_bank(data_dir: Optional[Path] = None) -> ContentBank:
    global _content_bank_instance
    if _content_bank_instance is None or data_dir is not None:
        _content_bank_instance = ContentBank(data_dir=data_dir)
    return _content_bank_instance
