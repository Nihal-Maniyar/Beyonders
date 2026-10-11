"""Pre/post assessment calculation and report generation engine."""

from typing import Dict, List

from pydantic import BaseModel

from learnloop.schemas.assessment import ConceptScore, PrePostReport


class AssessmentResponseItem(BaseModel):
    question_id: str
    concept_id: str
    is_correct: bool


def calculate_assessment_score(responses: List[AssessmentResponseItem]) -> tuple:
    """Calculate correct count, total count, and percentage."""
    if not responses:
        return 0, 0, 0.0
    correct = sum(1 for r in responses if r.is_correct)
    total = len(responses)
    pct = round((correct / total) * 100.0, 1)
    return correct, total, pct


def generate_pre_post_report(
    learner_id: str,
    pre_responses: List[AssessmentResponseItem],
    post_responses: List[AssessmentResponseItem],
    assessment_version: str = "fractions-v1.0",
) -> PrePostReport:
    """Generate comprehensive pre/post comparison report."""
    pre_correct, pre_total, pre_pct = calculate_assessment_score(pre_responses)
    post_correct, post_total, post_pct = calculate_assessment_score(post_responses)

    # Score change in percentage points (not percent of percent!)
    change_pp = round(post_pct - pre_pct, 1)

    # Calculate concept breakdown for C1, C2, C3
    concept_breakdown: Dict[str, ConceptScore] = {}
    all_concepts = sorted(list({r.concept_id for r in pre_responses + post_responses}))

    for cid in all_concepts:
        pre_c = [r for r in pre_responses if r.concept_id == cid]
        post_c = [r for r in post_responses if r.concept_id == cid]

        pre_c_corr, pre_c_tot, pre_c_pct = calculate_assessment_score(pre_c)
        post_c_corr, post_c_tot, post_c_pct = calculate_assessment_score(post_c)
        c_change_pp = round(post_c_pct - pre_c_pct, 1)

        concept_breakdown[cid] = ConceptScore(
            concept_id=cid,
            pre_correct=pre_c_corr,
            pre_total=pre_c_tot,
            post_correct=post_c_corr,
            post_total=post_c_tot,
            pre_percent=pre_c_pct,
            post_percent=post_c_pct,
            change_pp=c_change_pp,
        )

    return PrePostReport(
        learner_id=learner_id,
        assessment_version=assessment_version,
        paired_sample_count=1 if (pre_total == 6 and post_total == 6) else 0,
        pre_correct=pre_correct,
        pre_total=pre_total,
        pre_percent=pre_pct,
        post_correct=post_correct,
        post_total=post_total,
        post_percent=post_pct,
        score_change_pp=change_pp,
        concept_breakdown=concept_breakdown,
    )
