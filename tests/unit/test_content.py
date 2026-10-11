"""Unit tests for content bank validation."""

from learnloop.content.loader import FIXED_ASSESSMENT_QUESTION_IDS, get_content_bank


def test_content_bank_loads_and_validates():
    bank = get_content_bank()
    assert bank.chapter.chapter_id == "CH_FRACTIONS_01"
    assert len(bank.chapter.concepts) == 3
    assert len(bank.questions) >= 10
    assert len(bank.activities) >= 6
    assert len(bank.rubric.criteria) == 5


def test_fixed_assessment_questions_match_spec():
    bank = get_content_bank()
    questions = bank.get_fixed_assessment_questions()
    assert len(questions) == 6
    assert [q.question_id for q in questions] == FIXED_ASSESSMENT_QUESTION_IDS

    # 2 per concept C1, C2, C3
    c1_count = sum(1 for q in questions if q.concept_id == "C1")
    c2_count = sum(1 for q in questions if q.concept_id == "C2")
    c3_count = sum(1 for q in questions if q.concept_id == "C3")
    assert c1_count == 2
    assert c2_count == 2
    assert c3_count == 2


def test_question_references_valid_remediation_activities():
    bank = get_content_bank()
    for q in bank.questions.values():
        for act_id in q.remediation_activity_ids:
            act = bank.get_activity(act_id)
            assert act is not None
            assert act.activity_id == act_id
