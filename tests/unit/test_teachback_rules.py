"""Unit tests for teach-back rubric evaluation."""

from learnloop.domain.teachback_rules import evaluate_teachback_text
from learnloop.schemas.teachback import CriterionStatus


def test_acceptance_test_f_partial_teach_back():
    # Student explains R1 (numerator/denominator) and R2 (equal-sized parts), but not R4 or R5
    explanation = (
        "The denominator is the total number of equal parts that a whole is divided into. "
        "The numerator tells how many of those equal-sized pieces we have on our plate."
    )
    evaluation = evaluate_teachback_text(explanation)

    assert len(evaluation.criterion_results) == 5
    crit_map = {r.criterion_id: r.status for r in evaluation.criterion_results}

    assert crit_map["R1"] == CriterionStatus.DEMONSTRATED
    assert crit_map["R2"] == CriterionStatus.DEMONSTRATED
    assert crit_map["R4"] == CriterionStatus.NOT_DEMONSTRATED
    assert crit_map["R5"] == CriterionStatus.NOT_DEMONSTRATED

    # Separation: "not_demonstrated" vs "incorrect"
    assert crit_map["R4"] != CriterionStatus.INCORRECT

    # Points: R1(1.0) + R2(1.0) = 2.0 / 5.0 = 40.0%
    assert evaluation.earned_points >= 2.0
    assert evaluation.coverage_percent >= 40.0

    # Recommended concepts should include missing areas (C2, C3)
    assert "C2" in evaluation.recommended_concepts
    assert "C3" in evaluation.recommended_concepts


def test_full_teach_back_all_criteria_demonstrated():
    explanation = (
        "The denominator tells the total number of equal parts in a whole, and numerator counts the pieces. "
        "All parts must be equal-sized fair shares. "
        "Dividing into more pieces makes each piece smaller, so thirds are bigger pieces than fifths. "
        "To compare 2/5 and 2/3 with the same numerator, 2/3 is bigger because thirds are larger parts. "
        "Equivalent fractions like 1/2 and 2/4 represent the exact same amount because you multiply both top and bottom by 2."
    )
    evaluation = evaluate_teachback_text(explanation)
    assert len(evaluation.criterion_results) == 5
    crit_map = {r.criterion_id: r.status for r in evaluation.criterion_results}
    for cid in ["R1", "R2", "R3", "R4", "R5"]:
        assert crit_map[cid] == CriterionStatus.DEMONSTRATED
    assert evaluation.earned_points == 5.0
    assert evaluation.coverage_percent == 100.0
    assert len(evaluation.recommended_concepts) == 0


def test_short_teach_back_clarification_flag():
    evaluation = evaluate_teachback_text("pizza slice")
    assert evaluation.clarification_required is True
    assert evaluation.coverage_percent == 0.0
