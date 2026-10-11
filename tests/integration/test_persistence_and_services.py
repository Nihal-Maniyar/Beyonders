"""Integration tests for database persistence and application services."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learnloop.db.base import Base
from learnloop.domain.mastery_rules import MasteryStatus
from learnloop.repositories.learners import LearnerRepository
from learnloop.schemas.diagnosis import DiagnosisCode
from learnloop.services.assessment_service import AssessmentService
from learnloop.services.diagnosis_service import DiagnosisService
from learnloop.services.mastery_service import MasteryService
from learnloop.services.teachback_service import TeachBackService


@pytest.fixture
def test_db_session():
    """Create fresh in-memory SQLite database per test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_acceptance_test_g_persistence_across_sessions(test_db_session):
    learner_repo = LearnerRepository(test_db_session)
    learner_repo.get_or_create("learner_123", display_name="Test Student")
    test_db_session.commit()

    # Step 1: Record diagnosis attempt
    diag_service = DiagnosisService(test_db_session)
    diag_res = diag_service.diagnose_and_record(
        learner_id="learner_123",
        question_id="Q_C2_PRE_01",
        student_answer="A",
        reasoning_text="2/5 is larger because five is bigger than three.",
    )
    test_db_session.commit()

    assert diag_res.diagnosis_code == DiagnosisCode.M1
    assert diag_res.next_activity_id == "A_FRACTION_STRIPS"

    # Step 2: Open a fresh query from the same session to ensure it persisted
    mastery_service = MasteryService(test_db_session)
    masteries = mastery_service.get_learner_masteries("learner_123")
    assert "C2" in masteries
    assert masteries["C2"].evidence_attempt_count == 1
    assert masteries["C2"].status == MasteryStatus.DEVELOPING


def test_teachback_persistence(test_db_session):
    learner_repo = LearnerRepository(test_db_session)
    learner_repo.get_or_create("learner_456")
    test_db_session.commit()

    tb_service = TeachBackService(test_db_session)
    evaluation = tb_service.submit_and_evaluate(
        learner_id="learner_456",
        explanation="The denominator is the total number of equal parts. The numerator is how many parts you count.",
    )
    test_db_session.commit()

    assert evaluation.earned_points >= 1.0
    assert len(evaluation.criterion_results) == 5


def test_full_pre_post_assessment_flow(test_db_session):
    learner_repo = LearnerRepository(test_db_session)
    learner_repo.get_or_create("learner_789")
    test_db_session.commit()

    assess_service = AssessmentService(test_db_session)

    # 1. Pre-assessment: 6 items
    pre_run = assess_service.start_pre_assessment("learner_789")
    assess_service.record_answer(pre_run.id, "Q_C1_PRE_01", "A")  # correct
    assess_service.record_answer(pre_run.id, "Q_C1_PRE_02", "A")  # wrong
    assess_service.record_answer(pre_run.id, "Q_C2_PRE_01", "A")  # wrong
    assess_service.record_answer(pre_run.id, "Q_C2_PRE_02", "B")  # correct
    assess_service.record_answer(pre_run.id, "Q_C3_PRE_01", "A")  # correct
    assess_service.record_answer(pre_run.id, "Q_C3_PRE_02", "A")  # wrong
    assess_service.complete_run(pre_run.id)
    test_db_session.commit()

    # 2. Post-assessment: same 6 items, higher score
    post_run = assess_service.start_post_assessment("learner_789")
    assess_service.record_answer(post_run.id, "Q_C1_PRE_01", "A")  # correct
    assess_service.record_answer(post_run.id, "Q_C1_PRE_02", "B")  # correct
    assess_service.record_answer(post_run.id, "Q_C2_PRE_01", "B")  # correct
    assess_service.record_answer(post_run.id, "Q_C2_PRE_02", "B")  # correct
    assess_service.record_answer(post_run.id, "Q_C3_PRE_01", "A")  # correct
    assess_service.record_answer(post_run.id, "Q_C3_PRE_02", "B")  # correct
    assess_service.complete_run(post_run.id)
    test_db_session.commit()

    # 3. Report
    report = assess_service.get_pre_post_report("learner_789")
    assert report is not None
    assert report.pre_correct == 3
    assert report.post_correct == 6
    assert report.pre_percent == 50.0
    assert report.post_percent == 100.0
    assert report.score_change_pp == 50.0
    assert report.paired_sample_count == 1
