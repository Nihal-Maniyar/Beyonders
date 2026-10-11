"""Tutor service orchestrating lessons, practice, and remediation activities."""

from typing import List, Optional

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.schemas.content import Concept, Question, RemediationActivity


class TutorService:
    def __init__(self, content_bank: Optional[ContentBank] = None):
        self.bank = content_bank or get_content_bank()

    def get_all_concepts(self) -> List[Concept]:
        return self.bank.chapter.concepts

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        return self.bank.get_concept(concept_id)

    def get_remediation_activity(self, activity_id: str) -> Optional[RemediationActivity]:
        return self.bank.get_activity(activity_id)

    def get_practice_questions_for_concept(self, concept_id: str) -> List[Question]:
        return [
            q
            for q in self.bank.questions.values()
            if q.concept_id == concept_id
            and not q.is_transfer_question
            and not q.question_id.endswith("_PRE_01")
            and not q.question_id.endswith("_PRE_02")
        ]
