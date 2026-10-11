"""Idempotent database seeder for LearnLoop AI relational schema.

Seeds concepts, lessons, lesson_concepts, questions, question_options,
question_concepts, assessments, and assessment_questions from verified content bank.
"""

import json
from typing import Dict, Optional

from sqlalchemy.orm import Session

from learnloop.config import settings
from learnloop.db.models import (
    Assessment,
    AssessmentQuestion,
    Concept,
    Lesson,
    LessonConcept,
    Question,
    QuestionConcept,
    QuestionOption,
)
from learnloop.db.session import get_db_session, init_db


def seed_database(db: Optional[Session] = None) -> Dict[str, int]:
    """Idempotently seed the relational tables from verified JSON content files.

    Returns:
        Summary dict of counts seeded or verified.
    """
    if db is None:
        with get_db_session() as session:
            return _execute_seed(session)
    else:
        return _execute_seed(db)


def _execute_seed(session: Session) -> Dict[str, int]:
    data_dir = settings.data_dir
    chapter_path = data_dir / "fractions_chapter.json"
    questions_path = data_dir / "questions.json"

    if not chapter_path.exists() or not questions_path.exists():
        raise FileNotFoundError(f"Content files missing in {data_dir}")

    with open(chapter_path, "r", encoding="utf-8") as f:
        chapter_data = json.load(f)

    with open(questions_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    stats = {
        "concepts": 0,
        "lessons": 0,
        "questions": 0,
        "options": 0,
        "assessments": 0,
        "assessment_questions": 0,
    }

    # 1. Seed Concepts
    concept_map: Dict[str, Concept] = {}
    for c_data in chapter_data.get("concepts", []):
        code = c_data["concept_id"]
        concept = session.query(Concept).filter_by(code=code).first()
        if not concept:
            concept = Concept(
                code=code,
                name=c_data["title"],
                description=c_data.get("verified_explanation"),
            )
            session.add(concept)
            session.flush()
            stats["concepts"] += 1
        concept_map[code] = concept

    # 2. Seed Lessons & Lesson-Concept Links
    lesson_definitions = [
        {
            "code": "L_C1_UNDERSTANDING",
            "title": "Understanding Fractions: Parts of a Whole",
            "concept_code": "C1",
            "sequence_no": 1,
            "content": (
                "A fraction represents part of a whole divided into equal-sized parts. "
                "The denominator (bottom number) tells us how many equal parts make up the whole. "
                "The numerator (top number) counts how many of those equal parts are selected."
            ),
        },
        {
            "code": "L_C2_COMPARING",
            "title": "Comparing Fractions: Same Numerators & Denominators",
            "concept_code": "C2",
            "sequence_no": 2,
            "content": (
                "When comparing fractions with the same numerator, the fraction with the smaller denominator is larger, "
                "because dividing into fewer pieces makes each piece bigger! "
                "For example, 2/3 is greater than 2/5 because thirds are larger than fifths."
            ),
        },
        {
            "code": "L_C3_EQUIVALENT",
            "title": "Equivalent Fractions: Proportional Scaling",
            "concept_code": "C3",
            "sequence_no": 3,
            "content": (
                "Equivalent fractions represent the same quantity of a whole. "
                "You generate equivalent fractions by multiplying or dividing BOTH numerator and denominator "
                "by the same non-zero number. Adding a number changes the proportion!"
            ),
        },
    ]

    for l_data in lesson_definitions:
        lesson = session.query(Lesson).filter_by(code=l_data["code"]).first()
        if not lesson:
            lesson = Lesson(
                code=l_data["code"],
                title=l_data["title"],
                content=l_data["content"],
                sequence_no=l_data["sequence_no"],
                status="published",
            )
            session.add(lesson)
            session.flush()
            stats["lessons"] += 1

        # Link to concept
        c_obj = concept_map.get(l_data["concept_code"])
        if c_obj:
            lc = (
                session.query(LessonConcept)
                .filter_by(lesson_id=lesson.id, concept_id=c_obj.id)
                .first()
            )
            if not lc:
                session.add(LessonConcept(lesson_id=lesson.id, concept_id=c_obj.id))

    # 3. Seed Questions, Options, and Question-Concept Links
    question_map: Dict[str, Question] = {}
    for q_data in questions_data.get("questions", []):
        q_code = q_data["question_id"]
        question = session.query(Question).filter_by(code=q_code).first()
        if not question:
            question = Question(
                code=q_code,
                prompt=q_data["question_text"],
                question_type=q_data.get("question_type", "multiple_choice"),
                status="published",
                explanation=q_data.get("verified_explanation"),
            )
            session.add(question)
            session.flush()
            stats["questions"] += 1

            # Seed Options
            correct_key = q_data.get("correct_answer", "").strip().upper()
            for opt_raw in q_data.get("options", []):
                # Format: "A) The total number..."
                if ")" in opt_raw:
                    opt_key, opt_text = opt_raw.split(")", 1)
                    opt_key = opt_key.strip().upper()
                    opt_text = opt_text.strip()
                else:
                    opt_key = opt_raw[:1].upper()
                    opt_text = opt_raw.strip()

                is_correct = opt_key == correct_key
                option = QuestionOption(
                    question_id=question.id,
                    option_key=opt_key,
                    option_text=opt_text,
                    is_correct=is_correct,
                )
                session.add(option)
                stats["options"] += 1

            # Seed Concept Junction
            concept_code = q_data.get("concept_id")
            c_obj = concept_map.get(concept_code)
            if c_obj:
                session.add(QuestionConcept(question_id=question.id, concept_id=c_obj.id))

        question_map[q_code] = question

    session.flush()

    # 4. Seed Standard Assessments (pre, post, practice)
    assessments_meta = [
        {
            "code": "FRACTIONS_PRE",
            "title": "Fractions Diagnostic Pre-Assessment",
            "type": "pre",
            "question_codes": [
                "Q_C1_PRE_01",
                "Q_C1_PRE_02",
                "Q_C2_PRE_01",
                "Q_C2_PRE_02",
                "Q_C3_PRE_01",
                "Q_C3_PRE_02",
            ],
        },
        {
            "code": "FRACTIONS_POST",
            "title": "Fractions Progress Post-Assessment",
            "type": "post",
            "question_codes": [
                "Q_C1_PRE_01",
                "Q_C1_PRE_02",
                "Q_C2_PRE_01",
                "Q_C2_PRE_02",
                "Q_C3_PRE_01",
                "Q_C3_PRE_02",
            ],
        },
        {
            "code": "FRACTIONS_PRACTICE",
            "title": "Targeted Fractions Practice",
            "type": "practice",
            "question_codes": [
                "Q_C1_PRAC_01",
                "Q_C2_PRAC_01",
                "Q_C3_PRAC_01",
                "Q_C2_TRANSFER_01",
            ],
        },
    ]

    for a_data in assessments_meta:
        assessment = session.query(Assessment).filter_by(code=a_data["code"], version=1).first()
        if not assessment:
            assessment = Assessment(
                code=a_data["code"],
                title=a_data["title"],
                assessment_type=a_data["type"],
                version=1,
                is_active=True,
            )
            session.add(assessment)
            session.flush()
            stats["assessments"] += 1

        # Ensure questions are populated for assessment if missing
        existing_aq_count = (
            session.query(AssessmentQuestion).filter_by(assessment_id=assessment.id).count()
        )
        if existing_aq_count == 0:
            pos = 1
            for q_code in a_data["question_codes"]:
                q_obj = question_map.get(q_code)
                if q_obj:
                    aq = AssessmentQuestion(
                        assessment_id=assessment.id,
                        question_id=q_obj.id,
                        position=pos,
                        points_possible=1.0,
                    )
                    session.add(aq)
                    stats["assessment_questions"] += 1
                    pos += 1

    session.flush()
    return stats


if __name__ == "__main__":
    init_db()
    res = seed_database()
    print("Database seeding completed:", res)
