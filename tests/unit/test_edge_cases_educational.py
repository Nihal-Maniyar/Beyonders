"""Unit tests for educational and assessment edge cases.

Verifies:
- M3 (numerator-only comparison) diagnosis patterns.
- Answer normalization and null safety.
- Guard against invalid or unknown question IDs.
- Assessment response update idempotence / duplicate prevention.
- Pre-assessment confidentiality.
- Teach-back rubric edge-case boundaries.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learnloop.content.loader import get_content_bank
from learnloop.db.base import Base
from learnloop.domain.diagnosis_rules import (
    classify_reasoning,
    is_answer_correct,
    normalize_answer,
)
from learnloop.domain.teachback_rules import evaluate_teachback_text
from learnloop.repositories.assessments import AssessmentRepository
from learnloop.schemas.diagnosis import DiagnosisCode
from learnloop.schemas.teachback import CriterionStatus


def test_m3_numerator_only_comparison_patterns():
    """Verify various formulations of M3 numerator-only comparison reasoning."""
    # Pattern variation 1: 'only compared the numerators'
    res1 = classify_reasoning(
        question_id="Q_C2_TRANSFER_01",
        student_answer="A",
        reasoning_text="I only compared the numerators to decide which is bigger.",
    )
    assert res1.is_correct is False
    assert res1.diagnosis_code == DiagnosisCode.M3
    assert res1.next_activity_id == "A_NUMERATOR_DENOMINATOR_GRID"

    # Pattern variation 2: 'top numbers are bigger'
    res2 = classify_reasoning(
        question_id="Q_C2_TRANSFER_01",
        student_answer="A",
        reasoning_text="The top numbers are bigger so I picked 3/7.",
    )
    assert res2.is_correct is False
    assert res2.diagnosis_code == DiagnosisCode.M3

    # Pattern variation 3: 'numerator is larger'
    res3 = classify_reasoning(
        question_id="Q_C2_TRANSFER_01",
        student_answer="A",
        reasoning_text="The numerator is larger than the other one.",
    )
    assert res3.is_correct is False
    assert res3.diagnosis_code == DiagnosisCode.M3

    # Pattern variation 4: 'ignored the denominators'
    res4 = classify_reasoning(
        question_id="Q_C2_TRANSFER_01",
        student_answer="A",
        reasoning_text="I ignored the denominators and just looked at the tops.",
    )
    assert res4.is_correct is False
    assert res4.diagnosis_code == DiagnosisCode.M3


def test_m3_option_mapping_fallback_when_reasoning_minimal():
    """Verify that when reasoning is unspecific, question bank option mapping catches M3."""
    # In Q_C1_PRE_01, option B is mapped to M3 ("The number of parts selected or shaded")
    res = classify_reasoning(
        question_id="Q_C1_PRE_01",
        student_answer="B",
        reasoning_text="because that is what it is",
    )
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.M3
    assert res.next_activity_id == "A_PART_SIZE_EXPLORER"


def test_normalize_answer_edge_cases():
    """Verify normalize_answer handles whitespace, None, punctuation, and case."""
    assert normalize_answer(None) == ""
    assert normalize_answer("") == ""
    assert normalize_answer("   ") == ""
    assert normalize_answer("b") == "B"
    assert normalize_answer("  b  ") == "B"
    assert normalize_answer("B)") == "B"
    assert normalize_answer("b.") == "B"
    assert normalize_answer("c: some choice") == "C"
    assert normalize_answer("Option A") == "OPTION A"


def test_is_answer_correct_null_and_fuzzy_matching():
    """Verify is_answer_correct handles None, empty, whitespace, and accepted answers."""
    accepted = ["B", "2/3", "two thirds"]
    assert is_answer_correct("B", "B", accepted) is True
    assert is_answer_correct("b", "B", accepted) is True
    assert is_answer_correct("  B) 2/3  ", "B", accepted) is True
    assert is_answer_correct("2/3", "B", accepted) is True
    assert is_answer_correct("two thirds", "B", accepted) is True

    # Negative / edge cases
    assert is_answer_correct(None, "B", accepted) is False
    assert is_answer_correct("", "B", accepted) is False
    assert is_answer_correct("   ", "B", accepted) is False
    assert is_answer_correct("A", "B", accepted) is False


def test_classify_reasoning_unknown_question_raises():
    """Verify classify_reasoning raises ValueError for unknown question IDs."""
    with pytest.raises(ValueError, match="Unknown question_id"):
        classify_reasoning(question_id="INVALID_NON_EXISTENT_Q", student_answer="A")


def test_pre_assessment_content_confidentiality_guarantee():
    """Verify pre-assessment items protect answer keys from pre-completion exposure."""
    bank = get_content_bank()
    fixed_questions = bank.get_fixed_assessment_questions()
    assert len(fixed_questions) == 6

    for q in fixed_questions:
        # Questions must have verified explanations and correct answers stored in bank
        assert q.correct_answer in ["A", "B", "C", "D"]
        assert len(q.verified_explanation) > 10
        # Student-facing options do not contain the answer key label in option text
        for opt in q.options:
            assert "correct" not in opt.lower()
            assert "answer:" not in opt.lower()


def test_assessment_repository_record_response_duplicate_prevention():
    """Verify that recording a response twice for the same question updates rather than duplicates."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    repo = AssessmentRepository(session)
    run = repo.create_run(learner_id="learner_dup_test", phase="pre")
    session.commit()

    # First answer: student chooses "A"
    resp1 = repo.record_response(
        run_id=run.id,
        question_id="Q_C1_PRE_01",
        concept_id="C1",
        answer_text="A",
        is_correct=True,
    )
    session.commit()

    # Second answer: student changes choice to "B" within the same run
    resp2 = repo.record_response(
        run_id=run.id,
        question_id="Q_C1_PRE_01",
        concept_id="C1",
        answer_text="B",
        is_correct=False,
    )
    session.commit()

    responses = repo.get_run_responses(run.id)
    assert len(responses) == 1
    assert responses[0].id == resp1.id == resp2.id
    assert responses[0].answer_text == "B"
    assert responses[0].is_correct is False
    session.close()


def test_teachback_evaluation_boundary_cases():
    """Verify edge cases in teach-back evaluation."""
    # Case 1: Ultra short input (under 5 words)
    short_eval = evaluate_teachback_text("pizza has slices")
    assert short_eval.clarification_required is True
    assert short_eval.earned_points == 0.0
    assert short_eval.coverage_percent == 0.0
    assert len(short_eval.recommended_concepts) == 3

    # Case 2: Only explains R2 (equal parts) in enough words
    r2_eval = evaluate_teachback_text(
        "Fractions must always be divided into equal parts so everyone gets fair shares of the whole."
    )
    assert r2_eval.clarification_required is False
    r2_result = next(r for r in r2_eval.criterion_results if r.criterion_id == "R2")
    assert r2_result.status == CriterionStatus.DEMONSTRATED

    # Case 3: Explains that adding the same number to top and bottom is an additive error (R5 INCORRECT)
    r5_err_eval = evaluate_teachback_text(
        "To make equivalent fractions you can add the same number to top and bottom of the fraction."
    )
    r5_result = next(r for r in r5_err_eval.criterion_results if r.criterion_id == "R5")
    assert r5_result.status == CriterionStatus.INCORRECT
    assert "C3" in r5_err_eval.recommended_concepts
