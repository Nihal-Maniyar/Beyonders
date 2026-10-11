"""Unit tests verifying the 15 relational entities defined in context.md Section 16–20."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from learnloop.db.base import Base
from learnloop.db.models import (
    AnswerSubmission,
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    Concept,
    LearningSession,
    Lesson,
    LessonConcept,
    MisconceptionHypothesis,
    Question,
    QuestionConcept,
    QuestionOption,
    ReasoningResponse,
    TutoringInteraction,
    VoiceEvent,
    utc_now,
)


@pytest.fixture
def db_session():
    """Isolated in-memory SQLite database for relational model testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_all_15_entities_persist_and_relate(db_session):
    """Verify that all 15 relational entities can be created and linked correctly."""
    # 1. Learning Session
    session_obj = LearningSession(
        token_hash="hash_abc_123",
        status="active",
    )
    db_session.add(session_obj)
    db_session.flush()
    assert session_obj.id is not None
    assert session_obj.status == "active"

    # 2. Concept
    concept_c1 = Concept(
        code="C1",
        name="Equal Parts and Unit Fractions",
        description="Understanding fractions as fair shares.",
    )
    db_session.add(concept_c1)
    db_session.flush()

    # 3. Lesson & 4. LessonConcept
    lesson = Lesson(
        code="L_C1_01",
        title="Fair Shares with Pizza",
        content="When we divide a whole into equal parts...",
        sequence_no=1,
    )
    db_session.add(lesson)
    db_session.flush()

    lc = LessonConcept(lesson_id=lesson.id, concept_id=concept_c1.id)
    db_session.add(lc)
    db_session.flush()

    # 5. Question & 6. QuestionOption & 7. QuestionConcept
    question = Question(
        code="Q_C1_01",
        prompt="In 3/4, what does the denominator 4 represent?",
        question_type="multiple_choice",
        status="published",
    )
    db_session.add(question)
    db_session.flush()

    opt_a = QuestionOption(
        question_id=question.id,
        option_key="A",
        option_text="Total number of equal parts dividing the whole",
        is_correct=True,
    )
    opt_b = QuestionOption(
        question_id=question.id,
        option_key="B",
        option_text="Number of selected pieces",
        is_correct=False,
    )
    db_session.add_all([opt_a, opt_b])

    qc = QuestionConcept(question_id=question.id, concept_id=concept_c1.id)
    db_session.add(qc)
    db_session.flush()

    # 8. Assessment & 9. AssessmentQuestion
    assessment = Assessment(
        code="FRACTIONS_PRE",
        title="Diagnostic Pre-Assessment",
        assessment_type="pre",
        version=1,
        is_active=True,
    )
    db_session.add(assessment)
    db_session.flush()

    aq = AssessmentQuestion(
        assessment_id=assessment.id,
        question_id=question.id,
        position=1,
        points_possible=1.0,
    )
    db_session.add(aq)
    db_session.flush()

    # 10. AssessmentAttempt
    attempt = AssessmentAttempt(
        session_id=session_obj.id,
        assessment_id=assessment.id,
        attempt_no=1,
        status="in_progress",
    )
    db_session.add(attempt)
    db_session.flush()

    # 11. AnswerSubmission
    submission = AnswerSubmission(
        attempt_id=attempt.id,
        question_id=question.id,
        selected_option_id=opt_a.id,
        is_correct=True,
        points_awarded=1.0,
    )
    db_session.add(submission)
    db_session.flush()

    # 12. ReasoningResponse
    reasoning = ReasoningResponse(
        answer_submission_id=submission.id,
        sequence_no=1,
        response_text="The bottom number represents the total pieces in the whole.",
        input_mode="text",
    )
    db_session.add(reasoning)
    db_session.flush()

    # 13. TutoringInteraction
    interaction = TutoringInteraction(
        session_id=session_obj.id,
        sequence_no=1,
        role="tutor",
        interaction_type="explanation",
        content="Great job! The denominator indicates equal parts.",
    )
    db_session.add(interaction)
    db_session.flush()

    # 14. MisconceptionHypothesis
    hypothesis = MisconceptionHypothesis(
        session_id=session_obj.id,
        concept_id=concept_c1.id,
        evidence_answer_id=submission.id,
        code="NONE",
        description="Sound mathematical reasoning.",
        confidence=1.0,
        status="resolved",
    )
    db_session.add(hypothesis)
    db_session.flush()

    # 15. VoiceEvent
    voice_event = VoiceEvent(
        session_id=session_obj.id,
        interaction_id=interaction.id,
        provider="elevenlabs",
        direction="text_to_speech",
        status="succeeded",
        duration_ms=1850,
    )
    db_session.add(voice_event)
    db_session.commit()

    # Verify lookups and relationships
    saved_session = db_session.query(LearningSession).filter_by(id=session_obj.id).one()
    assert len(saved_session.relational_attempts) == 1
    assert len(saved_session.tutoring_interactions) == 1
    assert len(saved_session.misconceptions) == 1
    assert len(saved_session.voice_events) == 1

    saved_attempt = saved_session.relational_attempts[0]
    assert len(saved_attempt.answers) == 1
    assert len(saved_attempt.answers[0].reasonings) == 1
    assert saved_attempt.answers[0].reasonings[0].response_text.startswith("The bottom number")


def test_unique_constraints_enforced(db_session):
    """Verify composite uniqueness constraints across relational tables."""
    # Setup baseline session and assessment
    s = LearningSession(token_hash="hash_dup_test")
    db_session.add(s)

    a = Assessment(code="DUP_TEST", title="Dup Test", assessment_type="pre", version=1)
    db_session.add(a)

    q = Question(code="Q_DUP", prompt="Prompt?", question_type="multiple_choice")
    db_session.add(q)
    db_session.commit()

    # 1. Assessment (code, version) duplicate
    dup_a = Assessment(code="DUP_TEST", title="Dup Test 2", assessment_type="pre", version=1)
    db_session.add(dup_a)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # Re-fetch after rollback
    s = db_session.query(LearningSession).filter_by(token_hash="hash_dup_test").one()
    a = db_session.query(Assessment).filter_by(code="DUP_TEST").one()
    q = db_session.query(Question).filter_by(code="Q_DUP").one()

    # 2. Question option duplicate key
    opt1 = QuestionOption(question_id=q.id, option_key="A", option_text="Choice 1")
    opt2 = QuestionOption(question_id=q.id, option_key="A", option_text="Choice 2")
    db_session.add_all([opt1, opt2])
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # 3. Assessment Attempt duplicate (session, assessment, attempt_no)
    s = db_session.query(LearningSession).filter_by(token_hash="hash_dup_test").one()
    a = db_session.query(Assessment).filter_by(code="DUP_TEST").one()

    att1 = AssessmentAttempt(session_id=s.id, assessment_id=a.id, attempt_no=1)
    att2 = AssessmentAttempt(session_id=s.id, assessment_id=a.id, attempt_no=1)
    db_session.add_all([att1, att2])
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
