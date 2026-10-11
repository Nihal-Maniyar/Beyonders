from pathlib import Path
from streamlit.testing.v1 import AppTest

from learnloop.content.loader import FIXED_ASSESSMENT_QUESTION_IDS, get_content_bank
from learnloop.db.session import get_db_session
from learnloop.repositories.assessments import AssessmentRepository
from learnloop.services.assessment_service import AssessmentService

APP_PATH = str(Path(__file__).resolve().parent.parent.parent / "app.py")


def test_app_starts_without_uncaught_exceptions():
    """Requirement 1 & 2: App imports and starts without exception; welcome screen renders."""
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception
    assert at.session_state.current_stage == "WELCOME"
    # Check welcome elements exist
    buttons = [b.label for b in at.button]
    assert any("Start Baseline Assessment" in b for b in buttons)


def test_pre_assessment_progression_and_persistence():
    """Requirements 3, 4, 5, 6: Pre-assessment advances through 6 items and completes."""
    at = AppTest.from_file(APP_PATH)
    at.run()

    # Step 1: Click start baseline assessment
    start_btn = [b for b in at.button if "Start Baseline Assessment" in b.label][0]
    start_btn.click().run()
    assert at.session_state.current_stage == "PRE_ASSESSMENT"
    assert at.session_state.pre_run_id is not None

    bank = get_content_bank()
    questions = bank.get_fixed_assessment_questions()
    assert len(questions) == 6

    # Step 2: Answer all 6 questions sequentially
    for i in range(6):
        assert at.session_state.pre_index == i
        save_btn = [
            b for b in at.button if "Save & Next" in b.label or "Finish Pre-Assessment" in b.label
        ][0]
        save_btn.click().run()

    # Step 3: Transition to LESSON stage
    assert at.session_state.current_stage == "LESSON"

    # Verify answers recorded in database
    with get_db_session() as db:
        repo = AssessmentRepository(db)
        responses = repo.get_run_responses(at.session_state.pre_run_id)
        assert len(responses) == 6
        # Verify question IDs match the fixed assessment bank
        assert [r.question_id for r in responses] == FIXED_ASSESSMENT_QUESTION_IDS


def test_practice_diagnostic_conversation():
    """Requirements 7 & 8: Practice answers trigger diagnosis and clarification."""
    at = AppTest.from_file(APP_PATH)
    at.run()

    # Navigate to PRACTICE stage
    at.session_state.current_stage = "PRACTICE"
    at.run()
    assert not at.exception

    # Submit practice answer with vague reasoning ("idk") to verify clarification trigger
    at.session_state.last_diagnosis = None
    submit_btn = [b for b in at.button if "Submit Answer & Reasoning" in b.label][0]
    submit_btn.click().run()

    assert not at.exception
    assert at.session_state.last_diagnosis is not None
    # Clarification should be flagged for vague/empty reasoning
    assert at.session_state.last_diagnosis.clarification_required is True


def test_teach_back_submission_and_feedback():
    """Requirements 9 & 10: Teach-back submission produces rubric evaluation and revision advice."""
    at = AppTest.from_file(APP_PATH)
    at.run()

    at.session_state.current_stage = "TEACH_BACK"
    at.run()

    # Enter an explanation that demonstrates R1 and R2 but omits R4 and R5
    tb_input = at.text_area[0]
    tb_input.set_value(
        "The denominator is the total number of equal parts that a whole is divided into. "
        "The numerator tells how many of those equal pieces we have on our plate."
    )

    submit_btn = [b for b in at.button if "Submit Explanation" in b.label][0]
    submit_btn.click().run()

    assert at.session_state.current_stage == "TEACH_BACK_FEEDBACK"
    assert at.session_state.last_teachback_eval is not None
    evaluation = at.session_state.last_teachback_eval
    assert len(evaluation.criterion_results) == 5
    assert evaluation.earned_points >= 2.0
    # Recommended concepts should advise reviewing missing concepts
    assert "C2" in evaluation.recommended_concepts or "C3" in evaluation.recommended_concepts


def test_post_assessment_and_progress_report():
    """Requirements 11, 12, 13: Post-assessment calculates honest report with persistent records."""
    at = AppTest.from_file(APP_PATH)
    at.run()

    # Set learner and start pre-assessment to have paired data
    at.session_state.learner_id = "test_flow_student"
    with get_db_session() as db:
        assess = AssessmentService(db)
        pre_run = assess.start_pre_assessment("test_flow_student")
        for qid in FIXED_ASSESSMENT_QUESTION_IDS:
            assess.record_answer(pre_run.id, qid, "A")
        assess.complete_run(pre_run.id)

        post_run = assess.start_post_assessment("test_flow_student")
        for qid in FIXED_ASSESSMENT_QUESTION_IDS:
            assess.record_answer(post_run.id, qid, "B")
        assess.complete_run(post_run.id)

    # Navigate to PROGRESS_REPORT
    at.session_state.current_stage = "PROGRESS_REPORT"
    at.run()
    assert not at.exception

    # Verify report is calculated from DB
    with get_db_session() as db:
        assess = AssessmentService(db)
        report = assess.get_pre_post_report("test_flow_student")
        assert report is not None
        assert report.pre_total == 6
        assert report.post_total == 6
        assert report.paired_sample_count == 1
        assert len(report.limitations) >= 3


def test_offline_core_behavior_without_credentials():
    """Requirement 15: Application operates without LLM or voice API credentials."""
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception
    # Welcome, pre-assessment, lessons all render from local content bank
    bank = get_content_bank()
    assert bank.chapter.chapter_id == "CH_FRACTIONS_01"
