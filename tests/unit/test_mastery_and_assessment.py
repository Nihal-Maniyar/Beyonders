"""Unit tests for mastery calculation and pre/post assessment reporting."""

from learnloop.domain.assessment_rules import (
    AssessmentResponseItem,
    generate_pre_post_report,
)
from learnloop.domain.mastery_rules import (
    AttemptRecord,
    MasteryStatus,
    calculate_concept_mastery,
)
from learnloop.schemas.diagnosis import ReasoningStatus


def test_mastery_initial_state_not_assessed():
    summary = calculate_concept_mastery("C2", [])
    assert summary.status == MasteryStatus.NOT_ASSESSED
    assert summary.score == 0.0
    assert summary.evidence_attempt_count == 0


def test_mastery_developing_with_one_attempt():
    attempts = [
        AttemptRecord(
            attempt_id="att1",
            concept_id="C2",
            question_id="Q_C2_PRE_01",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
        )
    ]
    summary = calculate_concept_mastery("C2", attempts)
    assert summary.status == MasteryStatus.DEVELOPING
    assert summary.evidence_attempt_count == 1
    assert summary.distinct_question_count == 1


def test_mastery_repeated_answers_do_not_inflate_distinct_question_count():
    # 4 attempts on the SAME question
    attempts = [
        AttemptRecord(
            attempt_id=f"att_{i}",
            concept_id="C2",
            question_id="Q_C2_PRE_01",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
        )
        for i in range(4)
    ]
    summary = calculate_concept_mastery("C2", attempts)
    assert summary.distinct_question_count == 1
    # Since distinct_question_count < 3, cannot be mastered!
    assert summary.status == MasteryStatus.PRACTISING


def test_mastery_full_mastered_with_distinct_questions_and_transfer():
    attempts = [
        AttemptRecord(
            attempt_id="1",
            concept_id="C2",
            question_id="Q_C2_PRE_01",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
        ),
        AttemptRecord(
            attempt_id="2",
            concept_id="C2",
            question_id="Q_C2_PRE_02",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
        ),
        AttemptRecord(
            attempt_id="3",
            concept_id="C2",
            question_id="Q_C2_PRAC_01",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
        ),
        AttemptRecord(
            attempt_id="4",
            concept_id="C2",
            question_id="Q_C2_TRANSFER_01",
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID,
            is_transfer_question=True,
        ),
    ]
    summary = calculate_concept_mastery("C2", attempts)
    assert summary.distinct_question_count == 4
    assert summary.evidence_attempt_count == 4
    assert summary.transfer_passed is True
    assert summary.score >= 80.0
    assert summary.status == MasteryStatus.MASTERED


def test_acceptance_test_h_pre_post_assessment_report():
    # Pre: 3/6 = 50.0%
    pre_responses = [
        AssessmentResponseItem(question_id="Q_C1_PRE_01", concept_id="C1", is_correct=True),
        AssessmentResponseItem(question_id="Q_C1_PRE_02", concept_id="C1", is_correct=False),
        AssessmentResponseItem(question_id="Q_C2_PRE_01", concept_id="C2", is_correct=False),
        AssessmentResponseItem(question_id="Q_C2_PRE_02", concept_id="C2", is_correct=True),
        AssessmentResponseItem(question_id="Q_C3_PRE_01", concept_id="C3", is_correct=True),
        AssessmentResponseItem(question_id="Q_C3_PRE_02", concept_id="C3", is_correct=False),
    ]

    # Post: 5/6 = 83.3%
    post_responses = [
        AssessmentResponseItem(question_id="Q_C1_PRE_01", concept_id="C1", is_correct=True),
        AssessmentResponseItem(question_id="Q_C1_PRE_02", concept_id="C1", is_correct=True),
        AssessmentResponseItem(question_id="Q_C2_PRE_01", concept_id="C2", is_correct=True),
        AssessmentResponseItem(question_id="Q_C2_PRE_02", concept_id="C2", is_correct=True),
        AssessmentResponseItem(question_id="Q_C3_PRE_01", concept_id="C3", is_correct=True),
        AssessmentResponseItem(question_id="Q_C3_PRE_02", concept_id="C3", is_correct=False),
    ]

    report = generate_pre_post_report("test_learner", pre_responses, post_responses)
    assert report.pre_correct == 3
    assert report.pre_total == 6
    assert report.pre_percent == 50.0

    assert report.post_correct == 5
    assert report.post_total == 6
    assert report.post_percent == 83.3

    # Observed change: +33.3 percentage points!
    assert report.score_change_pp == 33.3
    assert report.paired_sample_count == 1

    # Limitations must be listed
    assert len(report.limitations) >= 3
    assert any("practice effect" in lim for lim in report.limitations)

    # Concept breakdown check
    assert "C1" in report.concept_breakdown
    assert "C2" in report.concept_breakdown
    assert report.concept_breakdown["C2"].change_pp == 50.0
