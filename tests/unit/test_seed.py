"""Unit tests verifying database seeding and idempotency."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learnloop.db.base import Base
from learnloop.db.models import (
    Assessment,
    AssessmentQuestion,
    Concept,
    Lesson,
    Question,
    QuestionOption,
)
from learnloop.db.seed import seed_database


@pytest.fixture
def clean_db():
    """In-memory database for seeding tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_seed_database_populates_all_tables(clean_db):
    """Verify first-time execution seeds concepts, lessons, assessments, questions, and options."""
    stats = seed_database(clean_db)
    clean_db.commit()

    assert stats["concepts"] == 3
    assert stats["lessons"] == 3
    assert stats["questions"] > 0
    assert stats["options"] > 0
    assert stats["assessments"] == 3
    assert stats["assessment_questions"] > 0

    # Verify Concepts C1, C2, C3
    c_codes = [c.code for c in clean_db.query(Concept).all()]
    assert set(c_codes) == {"C1", "C2", "C3"}

    # Verify Lessons
    lessons = clean_db.query(Lesson).all()
    assert len(lessons) == 3

    # Verify Assessments
    pre_assess = clean_db.query(Assessment).filter_by(code="FRACTIONS_PRE", version=1).one()
    assert pre_assess.assessment_type == "pre"
    assert len(pre_assess.questions) == 6

    # Verify Questions order in pre-assessment
    positions = [aq.position for aq in pre_assess.questions]
    assert positions == [1, 2, 3, 4, 5, 6]

    # Verify Question options
    sample_q = clean_db.query(Question).filter_by(code="Q_C1_PRE_01").one()
    assert len(sample_q.options) == 4
    correct_opts = [o for o in sample_q.options if o.is_correct]
    assert len(correct_opts) == 1
    assert correct_opts[0].option_key == "A"


def test_seed_database_is_idempotent(clean_db):
    """Verify repeated seed runs do not duplicate rows or crash."""
    # First run
    stats1 = seed_database(clean_db)
    clean_db.commit()
    initial_q_count = clean_db.query(Question).count()
    initial_c_count = clean_db.query(Concept).count()

    # Second run on same DB
    stats2 = seed_database(clean_db)
    clean_db.commit()

    # Assert no new records added
    assert stats2["concepts"] == 0
    assert stats2["lessons"] == 0
    assert stats2["questions"] == 0
    assert stats2["assessments"] == 0

    assert clean_db.query(Question).count() == initial_q_count
    assert clean_db.query(Concept).count() == initial_c_count

