"""Unit tests for misconception diagnosis engine."""

from learnloop.domain.diagnosis_rules import classify_reasoning
from learnloop.schemas.diagnosis import DiagnosisCode, ReasoningStatus


def test_acceptance_test_a_correct_answer_sound_reasoning():
    # Student compares 2/5 and 2/3 correctly
    res = classify_reasoning(
        question_id="Q_C2_PRE_01",
        student_answer="B",
        reasoning_text="Because thirds are bigger pieces than fifths, 2 thirds is greater than 2 fifths.",
    )
    assert res.is_correct is True
    assert res.reasoning_status == ReasoningStatus.VALID
    assert res.diagnosis_code == DiagnosisCode.NONE
    assert res.clarification_required is False
    assert res.next_activity_id is None


def test_acceptance_test_b_whole_number_bias_m1():
    # Student says 2/5 is larger because five is bigger than three
    res = classify_reasoning(
        question_id="Q_C2_PRE_01",
        student_answer="A",
        reasoning_text="2/5 is larger because five is bigger than three.",
    )
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.M1
    assert res.next_activity_id == "A_FRACTION_STRIPS"
    assert res.clarification_required is False
    assert "whole numbers" in res.evidence.lower() or "5 is bigger" in res.evidence.lower()


def test_acceptance_test_c_different_misconception_m2():
    # Student applies reversed denominator rule
    res = classify_reasoning(
        question_id="Q_C2_PRE_01",
        student_answer="A",
        reasoning_text="A fraction with a larger denominator is always larger.",
    )
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.M2
    assert res.next_activity_id == "A_PART_SIZE_EXPLORER"
    # Ensure Test B and Test C yield DIFFERENT activities and diagnoses!
    assert res.diagnosis_code != DiagnosisCode.M1
    assert res.next_activity_id != "A_FRACTION_STRIPS"


def test_acceptance_test_d_ambiguous_reasoning_u1():
    # Student gives wrong answer with no or vague reasoning
    res = classify_reasoning(question_id="Q_C2_PRE_01", student_answer="A", reasoning_text="idk")
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.U1
    assert res.clarification_required is True
    assert res.clarifying_question is not None
    assert len(res.clarifying_question) > 10


def test_acceptance_test_e_correct_answer_invalid_reasoning():
    # Student selects right answer (B) but says they guessed randomly
    res = classify_reasoning(
        question_id="Q_C2_PRE_01", student_answer="B", reasoning_text="I just guessed randomly"
    )
    assert res.is_correct is True
    assert res.reasoning_status == ReasoningStatus.UNCLEAR
    assert res.clarification_required is True


def test_misconception_m4_invalid_equivalent_transformation():
    # Student claims adding 2 keeps it equivalent
    res = classify_reasoning(
        question_id="Q_C3_PRE_02",
        student_answer="A",
        reasoning_text="I added the same number to top and bottom.",
    )
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.M4
    assert res.next_activity_id == "A_PROPORTIONAL_SCALING"


def test_misconception_s1_arithmetic_slip():
    res = classify_reasoning(
        question_id="Q_C3_PRAC_01",
        student_answer="C",
        reasoning_text="I found common denominator but made a math mistake in multiplication.",
    )
    assert res.is_correct is False
    assert res.diagnosis_code == DiagnosisCode.S1
    assert res.next_activity_id == "A_ARITHMETIC_RETRY"
