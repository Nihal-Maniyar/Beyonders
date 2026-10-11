"""Teach-back evaluation rules based on approved rubric.

Evaluates student explanation against criteria R1-R5:
- R1: Explains numerator and denominator correctly
- R2: Understands that fraction parts must be equal-sized
- R3: Explains how number of equal parts affects each part's size
- R4: Compares fractions using a valid method
- R5: Explains equivalent fractions correctly

Scores:
- demonstrated: 1.0 point
- partial: 0.5 points
- incorrect: 0.0 points
- not_demonstrated: 0.0 points

Coverage percent = (earned_points / total_possible) * 100
"""

import re
from typing import List, Optional

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.schemas.teachback import (
    CriterionResult,
    CriterionStatus,
    TeachBackEvaluation,
)

POINT_MAP = {
    CriterionStatus.DEMONSTRATED: 1.0,
    CriterionStatus.PARTIAL: 0.5,
    CriterionStatus.INCORRECT: 0.0,
    CriterionStatus.NOT_DEMONSTRATED: 0.0,
}


def evaluate_teachback_text(
    explanation: str,
    content_bank: Optional[ContentBank] = None,
) -> TeachBackEvaluation:
    """Deterministic rubric evaluation of student teach-back explanation."""
    bank = content_bank or get_content_bank()
    rubric = bank.rubric
    clean_text = explanation.strip()
    lower_text = clean_text.lower()
    words = lower_text.split()

    # Ambiguity check for extremely short responses
    if len(words) < 5:
        results = [
            CriterionResult(
                criterion_id=c.criterion_id,
                status=CriterionStatus.NOT_DEMONSTRATED,
                evidence="Response was too brief to provide clear evidence.",
            )
            for c in rubric.criteria
        ]
        return TeachBackEvaluation(
            rubric_id=rubric.rubric_id,
            content_version=rubric.content_version,
            criterion_results=results,
            earned_points=0.0,
            possible_points=5.0,
            coverage_percent=0.0,
            overall_feedback=(
                "Your explanation was very short. Please explain in your own words what you learned "
                "about numerators, denominators, comparing fractions, and equivalent fractions."
            ),
            recommended_concepts=["C1", "C2", "C3"],
            clarification_required=True,
        )

    results: List[CriterionResult] = []
    recommended_concepts = set()

    # --- Criterion R1: Numerator & Denominator ---
    has_num = bool(re.search(r"\bnumerator\b|\btop\s*(number|part)\b", lower_text))
    has_den = bool(re.search(r"\bdenominator\b|\bbottom\s*(number|part)\b", lower_text))
    explains_parts = bool(
        re.search(
            r"\bparts\s*of\s*a\s*whole\b|\bhow\s*many\s*(equal\s*)?parts\b|\bdivided\s*into\b|\bpieces\b",
            lower_text,
        )
    )

    if has_num and has_den and explains_parts:
        r1_status = CriterionStatus.DEMONSTRATED
        r1_evidence = "Clearly explained both numerator (selected parts) and denominator (total equal parts dividing the whole)."
    elif (has_num or has_den) and explains_parts:
        r1_status = CriterionStatus.PARTIAL
        r1_evidence = (
            "Partially explained fraction parts or mentioned either numerator or denominator."
        )
    elif re.search(r"\bdenominator\s*is\s*just\s*a\s*number\b", lower_text):
        r1_status = CriterionStatus.INCORRECT
        r1_evidence = "Incorrect explanation of denominator role."
        recommended_concepts.add("C1")
    else:
        r1_status = CriterionStatus.NOT_DEMONSTRATED
        r1_evidence = "Did not explain what numerator or denominator mean."
        recommended_concepts.add("C1")
    results.append(CriterionResult(criterion_id="R1", status=r1_status, evidence=r1_evidence))

    # --- Criterion R2: Equal-sized parts ---
    has_equal = bool(
        re.search(
            r"\bequal(\s*-?\s*sized)?\b|\bsame\s*size\b|\bfair\s*shares?\b|\bevenly\b", lower_text
        )
    )
    claims_unequal_ok = bool(
        re.search(
            r"\bparts?\s*(can|do\s*not)\s*(be\s*)?different\s*sizes?\b|\bany\s*size\b", lower_text
        )
    )

    if claims_unequal_ok:
        r2_status = CriterionStatus.INCORRECT
        r2_evidence = "Incorrect claim that fraction parts do not need to be equal in size."
        recommended_concepts.add("C1")
    elif has_equal:
        r2_status = CriterionStatus.DEMONSTRATED
        r2_evidence = "Explicitly stated that fraction pieces must be of equal size or fair shares."
    else:
        r2_status = CriterionStatus.NOT_DEMONSTRATED
        r2_evidence = "Did not address the requirement that parts must be equal-sized."
        recommended_concepts.add("C1")
    results.append(CriterionResult(criterion_id="R2", status=r2_status, evidence=r2_evidence))

    # --- Criterion R3: Denominator vs Part Size ---
    has_more_parts_smaller = (
        bool(
            re.search(
                r"(more\s*(pieces|parts)|(bigger|larger)\s*denominator).*?(smaller|each\s*piece\s*smaller)",
                lower_text,
            )
        )
        or bool(
            re.search(
                r"(fewer\s*(pieces|parts)|(smaller|less)\s*denominator).*?(bigger|larger|each\s*piece\s*bigger)",
                lower_text,
            )
        )
        or bool(
            re.search(
                r"thirds\s*are\s*(bigger|larger)\s*than\s*fifths|fifths\s*are\s*smaller\s*than\s*thirds",
                lower_text,
            )
        )
    )
    has_reversed_den = bool(
        re.search(
            r"(more\s*(pieces|parts)|(bigger|larger)\s*denominator)\s*(means|makes|is)\s*(always\s*)?(bigger|larger|greater)",
            lower_text,
        )
    )

    if has_reversed_den and not has_more_parts_smaller:
        r3_status = CriterionStatus.INCORRECT
        r3_evidence = (
            "Applied reversed denominator rule, claiming more pieces make each piece larger."
        )
        recommended_concepts.add("C2")
    elif has_more_parts_smaller:
        r3_status = CriterionStatus.DEMONSTRATED
        r3_evidence = "Understands that cutting a whole into more pieces makes each piece smaller."
    elif re.search(r"\bpieces\s*change\s*size\b", lower_text):
        r3_status = CriterionStatus.PARTIAL
        r3_evidence = "Acknowledged relationship between partitions and size without specifying inverse direction."
    else:
        r3_status = CriterionStatus.NOT_DEMONSTRATED
        r3_evidence = "Did not explain how the number of equal parts affects individual part size."
        recommended_concepts.add("C2")
    results.append(CriterionResult(criterion_id="R3", status=r3_status, evidence=r3_evidence))

    # --- Criterion R4: Valid comparison method ---
    has_valid_compare = bool(
        re.search(
            r"\b(common\s*denominator|cross\s*multiply|fraction\s*strips?|benchmark|same\s*numerator|same\s*denominator)\b",
            lower_text,
        )
    ) or bool(
        re.search(
            r"(2/3\s*(is)?\s*(bigger|larger|greater)\s*(than)?\s*2/5|thirds\s*are\s*bigger\s*than\s*fifths)",
            lower_text,
        )
    )
    has_whole_number_bias = bool(
        re.search(r"\b5\s*is\s*bigger\s*than\s*3\s*so\s*2/5\s*is\s*bigger\b", lower_text)
    )

    if has_whole_number_bias:
        r4_status = CriterionStatus.INCORRECT
        r4_evidence = "Used whole-number bias to compare fractions."
        recommended_concepts.add("C2")
    elif has_valid_compare:
        r4_status = CriterionStatus.DEMONSTRATED
        r4_evidence = "Demonstrated a mathematically sound fraction comparison method."
    elif re.search(r"\bcompare\b|\blarger\b|\bsmaller\b", lower_text):
        r4_status = CriterionStatus.PARTIAL
        r4_evidence = (
            "Mentioned comparing fractions but did not demonstrate a complete valid method."
        )
    else:
        r4_status = CriterionStatus.NOT_DEMONSTRATED
        r4_evidence = "Did not explain how to compare fractions."
        recommended_concepts.add("C2")
    results.append(CriterionResult(criterion_id="R4", status=r4_status, evidence=r4_evidence))

    # --- Criterion R5: Equivalent fractions ---
    has_scaling = bool(
        re.search(
            r"(multiply|multiplied|multiplying|divide|dividing)\s*(both|top\s*and\s*bottom|numerator\s*and\s*denominator)",
            lower_text,
        )
    ) or bool(
        re.search(
            r"\b2/4\s*(equals?|is\s*the\s*same\s*as)\s*1/2\b|\bsame\s*amount\b|\bsame\s*value\b",
            lower_text,
        )
    )
    has_additive_equiv = bool(
        re.search(
            r"\badd(ing)?\s*(the\s*same)?\s*(number\s*)?to\s*(both|top\s*and\s*bottom)\b",
            lower_text,
        )
    )

    if has_additive_equiv:
        r5_status = CriterionStatus.INCORRECT
        r5_evidence = (
            "Incorrectly claimed that adding to top and bottom produces equivalent fractions."
        )
        recommended_concepts.add("C3")
    elif has_scaling:
        r5_status = CriterionStatus.DEMONSTRATED
        r5_evidence = (
            "Explained that equivalent fractions have equal value and scale proportionally."
        )
    elif re.search(r"\bequivalent\b", lower_text):
        r5_status = CriterionStatus.PARTIAL
        r5_evidence = (
            "Mentioned equivalent fractions but explanation of proportional scaling was partial."
        )
    else:
        r5_status = CriterionStatus.NOT_DEMONSTRATED
        r5_evidence = "Did not explain equivalent fractions."
        recommended_concepts.add("C3")
    results.append(CriterionResult(criterion_id="R5", status=r5_status, evidence=r5_evidence))

    # Calculate points and coverage
    earned = sum(POINT_MAP[r.status] for r in results)
    possible = 5.0
    coverage = round((earned / possible) * 100.0, 1)

    # Build grounded student feedback
    demonstrated_criteria = [
        r.criterion_id for r in results if r.status == CriterionStatus.DEMONSTRATED
    ]
    missing_criteria = [
        r.criterion_id for r in results if r.status == CriterionStatus.NOT_DEMONSTRATED
    ]
    incorrect_criteria = [r.criterion_id for r in results if r.status == CriterionStatus.INCORRECT]

    feedback_parts = []
    if demonstrated_criteria:
        feedback_parts.append(
            f"You demonstrated good understanding of {', '.join(demonstrated_criteria)}."
        )
    if partial_criteria := [r.criterion_id for r in results if r.status == CriterionStatus.PARTIAL]:
        feedback_parts.append(f"You partially showed concepts for {', '.join(partial_criteria)}.")
    if incorrect_criteria:
        feedback_parts.append(
            f"There were misconceptions identified in {', '.join(incorrect_criteria)}."
        )
    if missing_criteria:
        feedback_parts.append(
            f"You have not yet demonstrated {', '.join(missing_criteria)} in your explanation."
        )

    overall_feedback = (
        " ".join(feedback_parts) if feedback_parts else "Thank you for explaining your thinking."
    )

    return TeachBackEvaluation(
        rubric_id=rubric.rubric_id,
        content_version=rubric.content_version,
        criterion_results=results,
        earned_points=earned,
        possible_points=possible,
        coverage_percent=coverage,
        overall_feedback=overall_feedback,
        recommended_concepts=sorted(list(recommended_concepts)),
        clarification_required=False,
    )
