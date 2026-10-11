"""Deterministic diagnosis engine for mathematical misconceptions.

Implements rules for:
- M1: Whole-number bias
- M2: Reversed denominator rule
- M3: Numerator-only comparison
- M4: Invalid additive transformation for equivalent fractions
- S1: Calculation / arithmetic slip
- U1: Insufficient evidence (clarification required)
- NONE: Correct or non-misconception response
"""

import re
from typing import Optional

from learnloop.content.loader import ContentBank, get_content_bank
from learnloop.schemas.diagnosis import (
    Certainty,
    DiagnosisCode,
    DiagnosisResult,
    ReasoningStatus,
)

# Student-facing diagnostic explanations (learner friendly, not raw codes)
STUDENT_FEEDBACK_MAP = {
    DiagnosisCode.M1: (
        "It looks like you might be thinking of denominators like regular whole numbers. "
        "With fractions, dividing a whole into MORE pieces actually makes each piece SMALLER! "
        "Let's look at fraction strips together to see why 2/3 is bigger than 2/5."
    ),
    DiagnosisCode.M2: (
        "It seems you may have reversed the rule about denominators. "
        "Remember: when sharing the same whole, a larger denominator means the pizza is split "
        "among more people, so each slice is smaller, not larger."
    ),
    DiagnosisCode.M3: (
        "It looks like you compared only the top numbers (numerators) without considering the denominators. "
        "When the denominators are different, we have to account for the size of each piece before comparing."
    ),
    DiagnosisCode.M4: (
        "It appears you added the same number to the top and bottom. "
        "Adding does not keep fractions equivalent because it changes the proportion! "
        "Equivalent fractions require multiplying or dividing by the same number."
    ),
    DiagnosisCode.S1: (
        "Your approach and concept were right, but there seems to be a minor calculation or copying slip. "
        "Let's check the arithmetic step together."
    ),
    DiagnosisCode.U1: (
        "I need a little more information to understand your thinking. "
        "What method or rule did you use to choose that answer?"
    ),
    DiagnosisCode.NONE: (
        "Great reasoning! You correctly accounted for both the number of parts and their sizes."
    ),
}

# Remediation activity mappings
DEFAULT_ACTIVITY_MAP = {
    DiagnosisCode.M1: "A_FRACTION_STRIPS",
    DiagnosisCode.M2: "A_PART_SIZE_EXPLORER",
    DiagnosisCode.M3: "A_NUMERATOR_DENOMINATOR_GRID",
    DiagnosisCode.M4: "A_PROPORTIONAL_SCALING",
    DiagnosisCode.S1: "A_ARITHMETIC_RETRY",
    DiagnosisCode.U1: "A_REASONING_CLARIFICATION",
    DiagnosisCode.NONE: None,
}


def normalize_answer(ans: str) -> str:
    """Normalize answer string for exact or option matching."""
    if not ans:
        return ""
    cleaned = ans.strip()
    # If starts with "A)", "B)", etc.
    if len(cleaned) >= 2 and cleaned[1] in (")", ".", ":"):
        return cleaned[0].upper()
    return cleaned.upper()


def is_answer_correct(student_answer: str, correct_answer: str, accepted_answers: list) -> bool:
    """Check correctness against question key."""
    norm_student = normalize_answer(student_answer)
    norm_correct = normalize_answer(correct_answer)
    if norm_student == norm_correct:
        return True

    student_lower = student_answer.strip().lower()
    for acc in accepted_answers:
        if normalize_answer(acc) == norm_student:
            return True
        if acc.strip().lower() in student_lower:
            return True
    return False


def classify_reasoning(
    question_id: str,
    student_answer: str,
    reasoning_text: Optional[str] = None,
    content_bank: Optional[ContentBank] = None,
) -> DiagnosisResult:
    """Deterministic diagnosis rule evaluation matching Spec §7 and §8."""
    bank = content_bank or get_content_bank()
    question = bank.get_question(question_id)
    if not question:
        raise ValueError(f"Unknown question_id: {question_id}")

    correct = is_answer_correct(student_answer, question.correct_answer, question.accepted_answers)
    text = (reasoning_text or "").strip().lower()

    # Case 1: Answer is Correct
    if correct:
        # Check if student explicitly provided guessing or invalid reasoning
        guess_keywords = ["random", "guessed", "guess", "no idea", "lucky", "idk", "just picked"]
        if any(kw in text for kw in guess_keywords):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=True,
                reasoning_status=ReasoningStatus.UNCLEAR,
                diagnosis_code=DiagnosisCode.NONE,
                certainty=Certainty.MEDIUM,
                evidence="Learner stated they guessed or picked randomly.",
                clarification_required=True,
                clarifying_question="You got the right answer, but could you explain why that fraction is larger?",
                next_activity_id=None,
                student_feedback="You chose the right answer! Can you explain your reasoning so we can confirm your understanding?",
            )

        # Check if reasoning contains contradictory whole-number bias even though answer was correct
        if "5 is bigger" in text or "5 is larger" in text or "bigger denominator is bigger" in text:
            return DiagnosisResult(
                question_id=question_id,
                is_correct=True,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.M1,
                certainty=Certainty.MEDIUM,
                evidence="Learner arrived at correct option but applied whole-number or inverted logic.",
                clarification_required=True,
                clarifying_question="How did the denominator values help you compare the pieces?",
                next_activity_id="A_FRACTION_STRIPS",
                student_feedback="You picked the right option, but your reasoning mentions whole-number size. Let's make sure the concept is solid.",
            )

        # Valid reasoning
        return DiagnosisResult(
            question_id=question_id,
            is_correct=True,
            reasoning_status=ReasoningStatus.VALID if text else ReasoningStatus.NOT_ASSESSED,
            diagnosis_code=DiagnosisCode.NONE,
            certainty=Certainty.HIGH,
            evidence=f"Correct answer with valid reasoning: '{reasoning_text}'"
            if text
            else "Correct answer submitted.",
            clarification_required=False,
            clarifying_question=None,
            next_activity_id=None,
            student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.NONE],
        )

    # Case 2: Answer is Incorrect
    # Check if reasoning is empty or vague (U1)
    vague_phrases = [
        "",
        "idk",
        "i don't know",
        "i dont know",
        "no idea",
        "dunno",
        "not sure",
        "random",
        "just guessed",
    ]
    if not text or text in vague_phrases or len(text.split()) < 2:
        # Check if multiple choice option has deterministic mapping as initial hint, but require clarification
        norm_choice = normalize_answer(student_answer)
        mapped_diag = question.misconception_mappings.get(norm_choice)

        return DiagnosisResult(
            question_id=question_id,
            is_correct=False,
            reasoning_status=ReasoningStatus.UNCLEAR,
            diagnosis_code=DiagnosisCode.U1,
            certainty=Certainty.UNKNOWN,
            evidence=f"Student provided an incorrect answer without sufficient explanatory reasoning (choice {norm_choice} hint: {mapped_diag or 'none'}).",
            clarification_required=True,
            clarifying_question="What made you choose that answer? Please explain your thinking in a sentence or two.",
            next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.U1],
            student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.U1],
        )

    # Pattern M1: Whole-number bias
    m1_patterns = [
        r"\b5\s*(is)?\s*(bigger|larger|greater|more)\s*(than)?\s*3\b",
        r"\bfive\s*(is)?\s*(bigger|larger|greater|more)\s*(than)?\s*three\b",
        r"\b7\s*(is)?\s*(bigger|larger|greater|more)\s*(than)?\s*5\b",
        r"\b8\s*(is)?\s*(bigger|larger|greater|more)\s*(than)?\s*3\b",
        r"\bwhole\s*number\b",
        r"\bdenominator\s*is\s*(bigger|larger|greater)\s*(so|therefore|means)\s*(bigger|larger|greater)\b",
        r"\b2/5\s*(is)?\s*(bigger|larger)\s*because\s*(5|five)\b",
    ]
    for pat in m1_patterns:
        if re.search(pat, text):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=False,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.M1,
                certainty=Certainty.HIGH,
                evidence=f"Student explicitly compared denominator values as whole numbers: '{reasoning_text}'.",
                clarification_required=False,
                clarifying_question=None,
                next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.M1],
                student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.M1],
            )

    # Pattern M2: Reversed denominator rule
    m2_patterns = [
        r"\blarger\s*denominator\s*(is\s*)?always\s*(larger|bigger|greater)\b",
        r"\bbigger\s*denominator\s*(is\s*)?always\s*(larger|bigger|greater)\b",
        r"\bmore\s*parts\s*(means|makes)\s*(bigger|larger)\s*(pieces|slices|fraction)\b",
        r"\bdivided\s*into\s*more\s*pieces\s*means\s*more\b",
    ]
    for pat in m2_patterns:
        if re.search(pat, text):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=False,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.M2,
                certainty=Certainty.HIGH,
                evidence=f"Student applied reversed denominator rule: '{reasoning_text}'.",
                clarification_required=False,
                clarifying_question=None,
                next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.M2],
                student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.M2],
            )

    # Pattern M4: Invalid additive transformation
    m4_patterns = [
        r"\badd(ed|ing)?\s*(the\s*same)?\s*number\b",
        r"\bplus\s*[0-9]+\b",
        r"\badd(ed)?\s*[0-9]+\s*to\s*(top|numerator|both)\b",
        r"\badd(ed)?\s*same\s*to\s*top\s*and\s*bottom\b",
    ]
    for pat in m4_patterns:
        if re.search(pat, text):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=False,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.M4,
                certainty=Certainty.HIGH,
                evidence=f"Student asserted that adding to numerator and denominator preserves equivalence: '{reasoning_text}'.",
                clarification_required=False,
                clarifying_question=None,
                next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.M4],
                student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.M4],
            )

    # Pattern M3: Numerator-only comparison
    m3_patterns = [
        r"\bonly\s*(looked\s*at|compared)\s*(the\s*)?numerator\b",
        r"\bonly\s*(the\s*)?top\s*number\b",
        r"\btop\s*number\s*is\s*(bigger|larger)\b",
        r"\bignored\s*(the\s*)?denominator\b",
    ]
    for pat in m3_patterns:
        if re.search(pat, text):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=False,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.M3,
                certainty=Certainty.HIGH,
                evidence=f"Student compared numerators only while ignoring denominators: '{reasoning_text}'.",
                clarification_required=False,
                clarifying_question=None,
                next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.M3],
                student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.M3],
            )

    # Pattern S1: Likely calculation slip
    s1_patterns = [
        r"\bcalculation\b",
        r"\bcommon\s*denominator\b",
        r"\bmultiplied\s*wrong\b",
        r"\bmath\s*mistake\b",
        r"\btypo\b",
    ]
    for pat in s1_patterns:
        if re.search(pat, text):
            return DiagnosisResult(
                question_id=question_id,
                is_correct=False,
                reasoning_status=ReasoningStatus.INVALID,
                diagnosis_code=DiagnosisCode.S1,
                certainty=Certainty.MEDIUM,
                evidence=f"Student valid method with arithmetic/transcription slip: '{reasoning_text}'.",
                clarification_required=False,
                clarifying_question=None,
                next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.S1],
                student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.S1],
            )

    # Check option-level mapping from question bank if reasoning is unspecific
    norm_choice = normalize_answer(student_answer)
    mapped_code = question.misconception_mappings.get(norm_choice)
    if mapped_code and mapped_code in DiagnosisCode.__members__:
        diag = DiagnosisCode(mapped_code)
        act = (
            question.remediation_activity_ids[0]
            if question.remediation_activity_ids
            else DEFAULT_ACTIVITY_MAP[diag]
        )
        return DiagnosisResult(
            question_id=question_id,
            is_correct=False,
            reasoning_status=ReasoningStatus.INVALID,
            diagnosis_code=diag,
            certainty=Certainty.MEDIUM,
            evidence=f"Student chose option {norm_choice} aligned with {diag.value} mapping. Reasoning: '{reasoning_text}'.",
            clarification_required=False,
            clarifying_question=None,
            next_activity_id=act,
            student_feedback=STUDENT_FEEDBACK_MAP.get(diag, STUDENT_FEEDBACK_MAP[DiagnosisCode.U1]),
        )

    # Fallback: U1 Insufficient evidence
    return DiagnosisResult(
        question_id=question_id,
        is_correct=False,
        reasoning_status=ReasoningStatus.UNCLEAR,
        diagnosis_code=DiagnosisCode.U1,
        certainty=Certainty.UNKNOWN,
        evidence=f"Reasoning text '{reasoning_text}' does not clearly match known misconception patterns.",
        clarification_required=True,
        clarifying_question="Could you clarify how you compared these fractions? What steps did you follow?",
        next_activity_id=DEFAULT_ACTIVITY_MAP[DiagnosisCode.U1],
        student_feedback=STUDENT_FEEDBACK_MAP[DiagnosisCode.U1],
    )
