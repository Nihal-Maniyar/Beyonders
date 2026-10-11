"""SQLAlchemy 2.x ORM models for LearnLoop AI.

Implements all 15 relational entities defined in context.md Section 16–20:
1. learning_sessions
2. concepts
3. lessons
4. lesson_concepts
5. questions
6. question_options
7. question_concepts
8. assessments
9. assessment_questions
10. assessment_attempts
11. answer_submissions
12. reasoning_responses
13. tutoring_interactions
14. misconception_hypotheses
15. voice_events

Also preserves legacy entities (LearnerModel, AttemptModel, AssessmentRunModel, etc.)
for 100% backward compatibility with the independent Streamlit backup application (app.py).
"""

import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from learnloop.db.base import Base


def utc_now() -> datetime.datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


def default_expiry() -> datetime.datetime:
    """Default session expiry: 24 hours from creation."""
    return utc_now() + datetime.timedelta(hours=24)


def generate_uuid() -> str:
    """Generate string UUIDv4 for dialect-neutral primary keys."""
    return str(uuid.uuid4())


# =============================================================================
# 1. LEARNING SESSIONS (context.md Section 16 & 17)
# =============================================================================


class LearningSessionModel(Base):
    """Anonymous learning session tracking and lifecycle."""

    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    token_hash = Column(String(128), unique=True, nullable=True, index=True)
    status = Column(String(20), default="active", nullable=False)  # active, completed, expired

    # Lifecycle timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    expires_at = Column(DateTime, default=default_expiry, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Legacy fields preserved for app.py Streamlit backup
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=True, index=True
    )
    chapter_id = Column(String(50), default="CH_FRACTIONS_01", nullable=True)
    content_version = Column(String(20), default="fractions-v1.0", nullable=True)
    current_stage = Column(String(50), default="WELCOME", nullable=False)
    started_at = Column(DateTime, default=utc_now, nullable=True)

    # Legacy relationships
    learner = relationship("LearnerModel", back_populates="sessions")
    attempts = relationship("AttemptModel", back_populates="session", cascade="all, delete-orphan")

    # New relational relationships (context.md)
    relational_attempts = relationship(
        "AssessmentAttempt", back_populates="session", cascade="all, delete-orphan"
    )
    tutoring_interactions = relationship(
        "TutoringInteraction", back_populates="session", cascade="all, delete-orphan"
    )
    misconceptions = relationship(
        "MisconceptionHypothesis", back_populates="session", cascade="all, delete-orphan"
    )
    voice_events = relationship(
        "VoiceEvent", back_populates="session", cascade="all, delete-orphan"
    )


LearningSession = LearningSessionModel


# =============================================================================
# 2. CONCEPTS (context.md Section 16 & 17)
# =============================================================================


class Concept(Base):
    """Fraction concepts registry (e.g. C1, C2, C3)."""

    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    lessons = relationship("LessonConcept", back_populates="concept", cascade="all, delete-orphan")
    questions = relationship(
        "QuestionConcept", back_populates="concept", cascade="all, delete-orphan"
    )
    hypotheses = relationship("MisconceptionHypothesis", back_populates="concept")


# =============================================================================
# 3. LESSONS (context.md Section 16 & 17)
# =============================================================================


class Lesson(Base):
    """Instructional fraction lesson content."""

    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="published", nullable=False)  # draft, published, archived
    sequence_no = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    concepts = relationship("LessonConcept", back_populates="lesson", cascade="all, delete-orphan")


# =============================================================================
# 4. LESSON CONCEPTS JUNCTION (context.md Section 16 & 17)
# =============================================================================


class LessonConcept(Base):
    """Many-to-many relationship between lessons and concepts."""

    __tablename__ = "lesson_concepts"

    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    concept_id = Column(
        String(36), ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True
    )

    lesson = relationship("Lesson", back_populates="concepts")
    concept = relationship("Concept", back_populates="lessons")


# =============================================================================
# 5. QUESTIONS (context.md Section 16 & 17)
# =============================================================================


class Question(Base):
    """Question prompts, type, and pedagogical explanation."""

    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    question_type = Column(
        String(30), default="multiple_choice", nullable=False
    )  # multiple_choice, short_text
    status = Column(String(20), default="published", nullable=False)  # draft, published, archived
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    options = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )
    concepts = relationship(
        "QuestionConcept", back_populates="question", cascade="all, delete-orphan"
    )
    assessment_links = relationship("AssessmentQuestion", back_populates="question")
    answers = relationship("AnswerSubmission", back_populates="question")


# =============================================================================
# 6. QUESTION OPTIONS (context.md Section 16 & 17)
# =============================================================================


class QuestionOption(Base):
    """Answer choices for multiple choice questions with internal correctness flags."""

    __tablename__ = "question_options"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_key = Column(String(10), nullable=False)  # A, B, C, D
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    question = relationship("Question", back_populates="options")

    __table_args__ = (UniqueConstraint("question_id", "option_key", name="uq_question_option_key"),)


# =============================================================================
# 7. QUESTION CONCEPTS JUNCTION (context.md Section 16 & 17)
# =============================================================================


class QuestionConcept(Base):
    """Many-to-many relationship between questions and concepts."""

    __tablename__ = "question_concepts"

    question_id = Column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    concept_id = Column(
        String(36), ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True
    )

    question = relationship("Question", back_populates="concepts")
    concept = relationship("Concept", back_populates="questions")


# =============================================================================
# 8. ASSESSMENTS (context.md Section 16 & 17)
# =============================================================================


class Assessment(Base):
    """Versioned assessment definitions (pre, post, practice)."""

    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    assessment_type = Column(String(20), nullable=False)  # pre, post, practice
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    questions = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="AssessmentQuestion.position",
    )
    attempts = relationship("AssessmentAttempt", back_populates="assessment")

    __table_args__ = (UniqueConstraint("code", "version", name="uq_assessment_code_version"),)


# =============================================================================
# 9. ASSESSMENT QUESTIONS (context.md Section 16 & 17)
# =============================================================================


class AssessmentQuestion(Base):
    """Ordered question membership within an assessment version."""

    __tablename__ = "assessment_questions"

    assessment_id = Column(
        String(36), ForeignKey("assessments.id", ondelete="RESTRICT"), primary_key=True
    )
    question_id = Column(
        String(36), ForeignKey("questions.id", ondelete="RESTRICT"), primary_key=True
    )
    position = Column(Integer, nullable=False)
    points_possible = Column(Float, default=1.0, nullable=False)

    assessment = relationship("Assessment", back_populates="questions")
    question = relationship("Question", back_populates="assessment_links")

    __table_args__ = (UniqueConstraint("assessment_id", "position", name="uq_assessment_position"),)


# =============================================================================
# 10. ASSESSMENT ATTEMPTS (context.md Section 16 & 17)
# =============================================================================


class AssessmentAttempt(Base):
    """Session attempt record for an assessment."""

    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(
        String(36),
        ForeignKey("learning_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assessment_id = Column(
        String(36), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    attempt_no = Column(Integer, default=1, nullable=False)
    status = Column(
        String(20), default="in_progress", nullable=False
    )  # in_progress, completed, abandoned
    raw_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    session = relationship("LearningSessionModel", back_populates="relational_attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    answers = relationship(
        "AnswerSubmission", back_populates="attempt", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "session_id", "assessment_id", "attempt_no", name="uq_session_assessment_attempt"
        ),
        Index("idx_attempts_session_started", "session_id", "started_at"),
        Index("idx_attempts_assessment_status", "assessment_id", "status"),
    )


# =============================================================================
# 11. ANSWER SUBMISSIONS (context.md Section 16 & 17)
# =============================================================================


class AnswerSubmission(Base):
    """Student answer submission for a question in an attempt."""

    __tablename__ = "answer_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(
        String(36),
        ForeignKey("assessment_attempts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        String(36), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    selected_option_id = Column(
        String(36), ForeignKey("question_options.id", ondelete="RESTRICT"), nullable=True
    )
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Float, nullable=True)
    submitted_at = Column(DateTime, default=utc_now, nullable=False)

    attempt = relationship("AssessmentAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    selected_option = relationship("QuestionOption")
    reasonings = relationship(
        "ReasoningResponse", back_populates="answer", cascade="all, delete-orphan"
    )
    hypotheses = relationship("MisconceptionHypothesis", back_populates="evidence_answer")

    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),
        Index("idx_answers_attempt", "attempt_id"),
    )


# =============================================================================
# 12. REASONING RESPONSES (context.md Section 16 & 17)
# =============================================================================


class ReasoningResponse(Base):
    """Student explanations associated with an answer submission."""

    __tablename__ = "reasoning_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    answer_submission_id = Column(
        String(36),
        ForeignKey("answer_submissions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no = Column(Integer, default=1, nullable=False)
    response_text = Column(Text, nullable=False)
    input_mode = Column(String(30), default="text", nullable=False)  # text, speech_transcript
    created_at = Column(DateTime, default=utc_now, nullable=False)

    answer = relationship("AnswerSubmission", back_populates="reasonings")

    __table_args__ = (
        UniqueConstraint(
            "answer_submission_id", "sequence_no", name="uq_answer_reasoning_sequence"
        ),
        Index("idx_reasoning_answer", "answer_submission_id"),
    )


# =============================================================================
# 13. TUTORING INTERACTIONS (context.md Section 16 & 17)
# =============================================================================


class TutoringInteraction(Base):
    """Ordered event and dialogue history for the tutoring loop."""

    __tablename__ = "tutoring_interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(
        String(36),
        ForeignKey("learning_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)  # student, tutor, system
    interaction_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    session = relationship("LearningSessionModel", back_populates="tutoring_interactions")
    voice_events = relationship("VoiceEvent", back_populates="interaction")

    __table_args__ = (
        UniqueConstraint("session_id", "sequence_no", name="uq_session_interaction_sequence"),
        Index("idx_interactions_session", "session_id", "sequence_no"),
    )


# =============================================================================
# 14. MISCONCEPTION HYPOTHESES (context.md Section 16 & 17)
# =============================================================================


class MisconceptionHypothesis(Base):
    """Tentative diagnostic hypotheses and evidence tracking."""

    __tablename__ = "misconception_hypotheses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(
        String(36),
        ForeignKey("learning_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="RESTRICT"), nullable=True)
    evidence_answer_id = Column(
        String(36), ForeignKey("answer_submissions.id", ondelete="RESTRICT"), nullable=True
    )
    code = Column(String(20), nullable=False)  # M1, M2, M3, M4, S1, U1
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    status = Column(
        String(20), default="tentative", nullable=False
    )  # tentative, confirmed, resolved, rejected
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    session = relationship("LearningSessionModel", back_populates="misconceptions")
    concept = relationship("Concept", back_populates="hypotheses")
    evidence_answer = relationship("AnswerSubmission", back_populates="hypotheses")

    __table_args__ = (Index("idx_misconceptions_session_status", "session_id", "status"),)


# =============================================================================
# 15. VOICE EVENTS (context.md Section 16 & 17)
# =============================================================================


class VoiceEvent(Base):
    """Operational telemetry and audit log for ElevenLabs voice requests."""

    __tablename__ = "voice_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(
        String(36),
        ForeignKey("learning_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interaction_id = Column(
        String(36), ForeignKey("tutoring_interactions.id", ondelete="SET NULL"), nullable=True
    )
    provider = Column(String(50), default="elevenlabs", nullable=False)
    direction = Column(
        String(30), default="text_to_speech", nullable=False
    )  # text_to_speech, speech_to_text
    status = Column(String(20), nullable=False)  # requested, succeeded, failed, cancelled
    duration_ms = Column(Integer, nullable=True)
    error_code = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    session = relationship("LearningSessionModel", back_populates="voice_events")
    interaction = relationship("TutoringInteraction", back_populates="voice_events")

    __table_args__ = (Index("idx_voice_events_session", "session_id", "created_at"),)


# =============================================================================
# LEGACY MODELS PRESERVED FOR app.py STREAMLIT BACKUP
# =============================================================================


class LearnerModel(Base):
    """Legacy profile model for Streamlit demo runner."""

    __tablename__ = "learners"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    display_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)

    sessions = relationship(
        "LearningSessionModel", back_populates="learner", cascade="all, delete-orphan"
    )
    attempts = relationship("AttemptModel", back_populates="learner", cascade="all, delete-orphan")
    assessment_runs = relationship(
        "AssessmentRunModel", back_populates="learner", cascade="all, delete-orphan"
    )
    masteries = relationship(
        "ConceptMasteryModel", back_populates="learner", cascade="all, delete-orphan"
    )
    review_tasks = relationship(
        "ReviewTaskModel", back_populates="learner", cascade="all, delete-orphan"
    )


class AttemptModel(Base):
    """Legacy practice attempt model for Streamlit runner."""

    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id = Column(
        String(36),
        ForeignKey("learning_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question_id = Column(String(50), nullable=False, index=True)
    concept_id = Column(String(20), nullable=False, index=True)
    content_version = Column(String(20), nullable=False)
    response_text = Column(Text, nullable=False)
    reasoning_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    reasoning_status = Column(String(20), default="not_assessed", nullable=False)
    diagnosis_code = Column(String(10), nullable=True)
    diagnosis_certainty = Column(String(20), nullable=True)
    diagnosis_evidence = Column(Text, nullable=True)
    clarification_required = Column(Boolean, default=False, nullable=False)
    activity_id = Column(String(50), nullable=True)
    source = Column(String(20), default="typed", nullable=False)
    follow_up_to_attempt_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    learner = relationship("LearnerModel", back_populates="attempts")
    session = relationship("LearningSessionModel", back_populates="attempts")

    __table_args__ = (Index("ix_attempts_learner_concept", "learner_id", "concept_id"),)


class AssessmentRunModel(Base):
    """Legacy assessment run model for Streamlit runner."""

    __tablename__ = "assessment_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id = Column(
        String(36), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True
    )
    phase = Column(String(10), nullable=False)  # pre, post
    assessment_version = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    learner = relationship("LearnerModel", back_populates="assessment_runs")
    responses = relationship(
        "AssessmentResponseModel", back_populates="assessment_run", cascade="all, delete-orphan"
    )


class AssessmentResponseModel(Base):
    """Legacy assessment response model for Streamlit runner."""

    __tablename__ = "assessment_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_run_id = Column(
        String(36), ForeignKey("assessment_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id = Column(String(50), nullable=False)
    concept_id = Column(String(20), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=utc_now, nullable=False)

    assessment_run = relationship("AssessmentRunModel", back_populates="responses")

    __table_args__ = (UniqueConstraint("assessment_run_id", "question_id", name="uq_run_question"),)


class TeachBackSubmissionModel(Base):
    """Legacy teach-back submission model for Streamlit runner."""

    __tablename__ = "teachback_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id = Column(
        String(36), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True
    )
    content_version = Column(String(20), nullable=False)
    response_text = Column(Text, nullable=False)
    input_source = Column(String(20), default="typed", nullable=False)  # typed, speech_transcript
    created_at = Column(DateTime, default=utc_now, nullable=False)

    evaluation = relationship(
        "TeachBackEvaluationModel",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )


class TeachBackEvaluationModel(Base):
    """Legacy teach-back evaluation model for Streamlit runner."""

    __tablename__ = "teachback_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(
        String(36),
        ForeignKey("teachback_submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    rubric_version = Column(String(20), nullable=False)
    criterion_results_json = Column(Text, nullable=False)
    earned_points = Column(Float, nullable=False)
    possible_points = Column(Float, default=5.0, nullable=False)
    coverage_percent = Column(Float, nullable=False)
    overall_feedback = Column(Text, nullable=False)
    recommended_concepts_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    submission = relationship("TeachBackSubmissionModel", back_populates="evaluation")


class ConceptMasteryModel(Base):
    """Legacy mastery snapshot model for Streamlit runner."""

    __tablename__ = "concept_mastery"

    learner_id = Column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), primary_key=True)
    concept_id = Column(String(20), primary_key=True)
    status = Column(
        String(20), default="not_assessed", nullable=False
    )  # not_assessed, developing, practising, mastered
    score = Column(Float, default=0.0, nullable=False)
    evidence_attempt_count = Column(Integer, default=0, nullable=False)
    distinct_question_count = Column(Integer, default=0, nullable=False)
    transfer_passed = Column(Boolean, default=False, nullable=False)
    last_evidence_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    policy_version = Column(String(20), default="mastery-v1.0", nullable=False)

    learner = relationship("LearnerModel", back_populates="masteries")


class ReviewTaskModel(Base):
    """Legacy spaced review task model for Streamlit runner."""

    __tablename__ = "review_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    concept_id = Column(String(20), nullable=False)
    reason = Column(String(255), nullable=False)
    due_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="due", nullable=False)  # due, completed, dismissed
    source_attempt_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    learner = relationship("LearnerModel", back_populates="review_tasks")
