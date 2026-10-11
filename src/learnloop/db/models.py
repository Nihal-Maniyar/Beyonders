"""SQLAlchemy 2.x ORM models for LearnLoop AI."""

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
    return datetime.datetime.now(datetime.timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class LearnerModel(Base):
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


class LearningSessionModel(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(
        String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chapter_id = Column(String(50), nullable=False)
    content_version = Column(String(20), nullable=False)
    current_stage = Column(String(50), default="WELCOME", nullable=False)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(
        String(20), default="in_progress", nullable=False
    )  # in_progress, completed, abandoned

    learner = relationship("LearnerModel", back_populates="sessions")
    attempts = relationship("AttemptModel", back_populates="session", cascade="all, delete-orphan")


class AttemptModel(Base):
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
