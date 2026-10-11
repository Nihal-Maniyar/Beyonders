"""Integration tests verifying persistence isolation, multi-tenant isolation, and recovery.

Verifies:
- Complete isolation between multiple concurrent learners (Learner A vs Learner B).
- Database transaction atomicity and rollback safety.
- Persistent SQLite on-disk session recovery.
- Review task queue isolation and completion state lifecycle.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learnloop.db.base import Base
from learnloop.domain.mastery_rules import MasteryStatus
from learnloop.repositories.attempts import AttemptRepository
from learnloop.repositories.learners import LearnerRepository
from learnloop.schemas.diagnosis import DiagnosisCode
from learnloop.services.assessment_service import AssessmentService
from learnloop.services.diagnosis_service import DiagnosisService
from learnloop.services.mastery_service import MasteryService
from learnloop.services.review_service import ReviewService
from learnloop.services.teachback_service import TeachBackService


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_multi_learner_data_isolation(memory_db):
    """Verify that multiple learners' data remain strictly isolated without cross-talk."""
    learner_repo = LearnerRepository(memory_db)
    alice = learner_repo.get_or_create("learner_alice", display_name="Alice")
    bob = learner_repo.get_or_create("learner_bob", display_name="Bob")
    memory_db.commit()

    assess_service = AssessmentService(memory_db)
    diag_service = DiagnosisService(memory_db)
    tb_service = TeachBackService(memory_db)
    mastery_service = MasteryService(memory_db)
    review_service = ReviewService(memory_db)
    attempt_repo = AttemptRepository(memory_db)

    # 1. Alice pre-assessment (1 correct)
    alice_pre = assess_service.start_pre_assessment(alice.id)
    assess_service.record_answer(alice_pre.id, "Q_C1_PRE_01", "A")
    assess_service.record_answer(alice_pre.id, "Q_C1_PRE_02", "A")
    assess_service.complete_run(alice_pre.id)

    # 2. Bob pre-assessment (2 correct)
    bob_pre = assess_service.start_post_assessment(bob.id)  # post or pre
    assess_service.record_answer(bob_pre.id, "Q_C1_PRE_01", "A")
    assess_service.record_answer(bob_pre.id, "Q_C1_PRE_02", "B")
    assess_service.complete_run(bob_pre.id)
    memory_db.commit()

    # 3. Practice Attempts
    # Alice demonstrates M1 misconception
    alice_diag = diag_service.diagnose_and_record(
        learner_id=alice.id,
        question_id="Q_C2_PRE_01",
        student_answer="A",
        reasoning_text="5 is bigger than 3 so 2/5 is bigger",
    )
    # Bob demonstrates valid reasoning
    bob_diag = diag_service.diagnose_and_record(
        learner_id=bob.id,
        question_id="Q_C2_PRE_01",
        student_answer="B",
        reasoning_text="Thirds are bigger pieces than fifths so 2/3 is greater",
    )
    memory_db.commit()

    assert alice_diag.diagnosis_code == DiagnosisCode.M1
    assert bob_diag.diagnosis_code == DiagnosisCode.NONE

    # 4. Teach-Back
    alice_tb = tb_service.submit_and_evaluate(
        learner_id=alice.id,
        explanation="The top number is numerator and bottom is denominator but bigger denominator means bigger.",
    )
    bob_tb = tb_service.submit_and_evaluate(
        learner_id=bob.id,
        explanation=(
            "The numerator is how many equal parts we have and denominator is total equal parts. "
            "Fraction parts must always be equal sized. When denominator is larger, each slice is smaller. "
            "Thirds are bigger than fifths. Equivalent fractions scale by multiplying top and bottom."
        ),
    )
    memory_db.commit()

    assert alice_tb.earned_points < bob_tb.earned_points

    # 5. Review tasks
    review_service.schedule_misconception_review(
        learner_id=alice.id,
        concept_id="C2",
        diagnosis_code=DiagnosisCode.M1.value,
    )
    memory_db.commit()

    # --- VERIFY ISOLATION ---
    # Attempts isolation
    alice_attempts = attempt_repo.get_learner_attempts(alice.id)
    bob_attempts = attempt_repo.get_learner_attempts(bob.id)
    assert len(alice_attempts) == 1
    assert len(bob_attempts) == 1
    assert alice_attempts[0].learner_id == alice.id
    assert bob_attempts[0].learner_id == bob.id
    assert alice_attempts[0].diagnosis_code == DiagnosisCode.M1.value
    assert bob_attempts[0].diagnosis_code == DiagnosisCode.NONE.value

    # Review tasks isolation
    alice_tasks = review_service.get_due_tasks(alice.id)
    bob_tasks = review_service.get_due_tasks(bob.id)
    assert len(alice_tasks) == 1
    assert len(bob_tasks) == 0

    # Mastery isolation
    alice_masteries = mastery_service.get_learner_masteries(alice.id)
    bob_masteries = mastery_service.get_learner_masteries(bob.id)
    assert alice_masteries["C2"].status == MasteryStatus.DEVELOPING
    assert bob_masteries["C2"].status == MasteryStatus.DEVELOPING


def test_database_transaction_atomicity_and_rollback(memory_db):
    """Verify that failed transactions roll back cleanly without polluting state."""
    learner_repo = LearnerRepository(memory_db)
    learner = learner_repo.get_or_create("learner_rollback_test", display_name="Rollback Test")
    memory_db.commit()

    # Pre-condition check: learner exists, zero attempts
    attempt_repo = AttemptRepository(memory_db)
    assert len(attempt_repo.get_learner_attempts(learner.id)) == 0

    # Simulate an operation that encounters an error mid-transaction
    try:
        attempt_repo.record_attempt(
            learner_id=learner.id,
            question_id="Q_C1_PRE_01",
            concept_id="C1",
            response_text="A",
            is_correct=True,
            reasoning_status="VALID",
            diagnosis_code="NONE",
            diagnosis_certainty="HIGH",
            diagnosis_evidence="Valid attempt before simulated crash",
        )
        # Simulate unexpected system failure before commit
        raise RuntimeError("Simulated mid-transaction failure")
    except RuntimeError:
        memory_db.rollback()

    # Verify atomicity: uncommitted attempt was rolled back
    attempts_after_rollback = attempt_repo.get_learner_attempts(learner.id)
    assert len(attempts_after_rollback) == 0


def test_sqlite_disk_file_persistence_and_session_recovery(tmp_path: Path):
    """Verify state recovery across fresh engine and session connections to an on-disk SQLite file."""
    db_file = tmp_path / "test_session_recovery.db"
    db_url = f"sqlite:///{db_file}"

    # SESSION 1: Create state and commit
    engine1 = create_engine(db_url, echo=False)
    Base.metadata.create_all(bind=engine1)
    Session1 = sessionmaker(bind=engine1)
    session1 = Session1()

    learner_repo1 = LearnerRepository(session1)
    learner1 = learner_repo1.get_or_create("disk_learner_01", display_name="Disk Learner")

    diag_service1 = DiagnosisService(session1)
    diag_service1.diagnose_and_record(
        learner_id=learner1.id,
        question_id="Q_C2_PRE_01",
        student_answer="A",
        reasoning_text="5 is bigger than 3 so 2/5 is bigger",
    )

    assess_service1 = AssessmentService(session1)
    pre_run1 = assess_service1.start_pre_assessment(learner1.id)
    assess_service1.record_answer(pre_run1.id, "Q_C1_PRE_01", "A")
    assess_service1.complete_run(pre_run1.id)
    pre_run_id = pre_run1.id

    session1.commit()
    session1.close()
    engine1.dispose()

    # SESSION 2: Open a brand new engine and session to the same file
    engine2 = create_engine(db_url, echo=False)
    Session2 = sessionmaker(bind=engine2)
    session2 = Session2()

    learner_repo2 = LearnerRepository(session2)
    recovered_learner = learner_repo2.get_by_id("disk_learner_01")
    assert recovered_learner is not None
    assert recovered_learner.display_name == "Disk Learner"

    attempt_repo2 = AttemptRepository(session2)
    recovered_attempts = attempt_repo2.get_learner_attempts("disk_learner_01")
    assert len(recovered_attempts) == 1
    assert recovered_attempts[0].question_id == "Q_C2_PRE_01"
    assert recovered_attempts[0].diagnosis_code == DiagnosisCode.M1.value

    mastery_service2 = MasteryService(session2)
    recovered_masteries = mastery_service2.get_learner_masteries("disk_learner_01")
    assert "C2" in recovered_masteries
    assert recovered_masteries["C2"].evidence_attempt_count == 1

    assess_service2 = AssessmentService(session2)
    latest_run = assess_service2.repo.get_latest_completed_run("disk_learner_01", phase="pre")
    assert latest_run is not None
    assert latest_run.id == pre_run_id

    session2.close()
    engine2.dispose()


def test_review_schedule_service_lifecycle(memory_db):
    """Verify review task lifecycle from creation to due querying and completion."""
    learner_repo = LearnerRepository(memory_db)
    learner = learner_repo.get_or_create("learner_review_lifecycle")
    memory_db.commit()

    review_service = ReviewService(memory_db)
    task = review_service.schedule_misconception_review(
        learner_id=learner.id,
        concept_id="C1",
        diagnosis_code="M1",
    )
    memory_db.commit()

    # Query due tasks
    due_tasks = review_service.get_due_tasks(learner.id)
    assert len(due_tasks) == 1
    assert due_tasks[0].id == task.id
    assert due_tasks[0].status == "due"

    # Complete task
    completed = review_service.repo.mark_completed(task.id)
    memory_db.commit()
    assert completed is not None
    assert completed.status == "completed"

    # Verify no longer returned in get_due_tasks
    remaining_due = review_service.get_due_tasks(learner.id)
    assert len(remaining_due) == 0
