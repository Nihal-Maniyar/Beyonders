"""Tutoring & Socratic Dialogue Orchestration Service.

Authoritatively coordinates:
1. Deterministic misconception diagnosis (M1-M4, S1, U1) from domain rules.
2. Teach-back rubric evaluation (R1-R5) from domain rules.
3. Relational persistence of reasoning explanations, misconception hypotheses,
   and ordered Socratic tutoring interactions.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from learnloop.db.models import (
    AnswerSubmission,
    Assessment,
    AssessmentAttempt,
    LearningSessionModel,
    MisconceptionHypothesis,
    Question,
    QuestionOption,
    ReasoningResponse,
    TutoringInteraction,
    utc_now,
)
from learnloop.domain.diagnosis_rules import classify_reasoning
from learnloop.domain.teachback_rules import evaluate_teachback_text


class TutoringService:
    """Coordinates deterministic Socratic tutoring interactions and diagnostics."""

    @staticmethod
    def _get_next_interaction_sequence(db: Session, session_id: str) -> int:
        """Get next sequence number for tutoring interactions in a session."""
        max_seq = (
            db.query(func.max(TutoringInteraction.sequence_no))
            .filter(TutoringInteraction.session_id == session_id)
            .scalar()
        )
        return (max_seq or 0) + 1

    @staticmethod
    def record_reasoning(
        db: Session,
        session_id: str,
        answer_submission_id: str,
        response_text: str,
        input_mode: str = "text",
    ) -> Dict[str, Any]:
        """Record a student's reasoning explanation for a previously submitted answer.

        Verifies that the target answer belongs to an attempt owned by session_id.
        """
        # 1. Fetch submission with attempt ownership verification
        submission = (
            db.query(AnswerSubmission)
            .join(
                AssessmentAttempt,
                AnswerSubmission.attempt_id == AssessmentAttempt.id,
            )
            .filter(
                AnswerSubmission.id == answer_submission_id,
                AssessmentAttempt.session_id == session_id,
            )
            .first()
        )
        if not submission:
            # Check if answer exists under another session to distinguish 403 vs 404
            other = (
                db.query(AnswerSubmission)
                .filter(AnswerSubmission.id == answer_submission_id)
                .first()
            )
            if other:
                raise PermissionError(
                    "Access denied: answer submission belongs to another session."
                )
            raise ValueError(f"Answer submission '{answer_submission_id}' not found.")

        # 2. Compute sequence_no for this answer's reasoning responses
        max_seq = (
            db.query(func.max(ReasoningResponse.sequence_no))
            .filter(ReasoningResponse.answer_submission_id == answer_submission_id)
            .scalar()
        )
        seq_no = (max_seq or 0) + 1

        # 3. Create ReasoningResponse record
        reasoning = ReasoningResponse(
            answer_submission_id=answer_submission_id,
            sequence_no=seq_no,
            response_text=response_text.strip(),
            input_mode=input_mode,
            created_at=utc_now(),
        )
        db.add(reasoning)

        # 4. Run deterministic diagnosis on question + answer + reasoning
        q = db.query(Question).filter(Question.id == submission.question_id).first()
        diagnosis_data: Optional[Dict[str, Any]] = None
        if q:
            ans_text = submission.answer_text
            if not ans_text and submission.selected_option_id:
                opt = (
                    db.query(QuestionOption)
                    .filter(QuestionOption.id == submission.selected_option_id)
                    .first()
                )
                if opt:
                    ans_text = opt.option_key

            diag_result = classify_reasoning(
                question_id=q.code or q.id,
                student_answer=ans_text or "",
                reasoning_text=response_text,
            )
            diagnosis_data = diag_result.model_dump()

            # Record hypothesis if misconception detected
            if diag_result.diagnosis_code.value in ("M1", "M2", "M3", "M4", "S1"):
                concept_id = None
                if q.concepts:
                    concept_id = q.concepts[0].concept_id

                existing_hyp = (
                    db.query(MisconceptionHypothesis)
                    .filter(
                        MisconceptionHypothesis.session_id == session_id,
                        MisconceptionHypothesis.code == diag_result.diagnosis_code.value,
                        MisconceptionHypothesis.status.in_(["tentative", "confirmed"]),
                    )
                    .first()
                )
                if existing_hyp:
                    existing_hyp.evidence_answer_id = submission.id
                    existing_hyp.description = diag_result.student_feedback
                    existing_hyp.updated_at = utc_now()
                else:
                    new_hyp = MisconceptionHypothesis(
                        session_id=session_id,
                        concept_id=concept_id,
                        evidence_answer_id=submission.id,
                        code=diag_result.diagnosis_code.value,
                        description=diag_result.student_feedback,
                        confidence=0.9 if diag_result.certainty.value == "high" else 0.7,
                        status="tentative",
                        created_at=utc_now(),
                        updated_at=utc_now(),
                    )
                    db.add(new_hyp)

        # 5. Log student tutoring interaction
        int_seq = TutoringService._get_next_interaction_sequence(db, session_id)
        student_int = TutoringInteraction(
            session_id=session_id,
            sequence_no=int_seq,
            role="student",
            interaction_type="reasoning_response",
            content=response_text.strip(),
            created_at=utc_now(),
        )
        db.add(student_int)

        db.flush()

        return {
            "id": reasoning.id,
            "answer_submission_id": reasoning.answer_submission_id,
            "sequence_no": reasoning.sequence_no,
            "response_text": reasoning.response_text,
            "input_mode": reasoning.input_mode,
            "created_at": reasoning.created_at.isoformat(),
            "diagnosis": diagnosis_data,
        }

    @staticmethod
    def diagnose_practice(
        db: Session,
        session_id: str,
        question_identifier: str,
        student_answer: str,
        reasoning_text: Optional[str] = None,
        input_mode: str = "text",
    ) -> Dict[str, Any]:
        """Diagnose a practice question answer + reasoning deterministically and persist records."""
        # 1. Verify session is active
        session_obj = (
            db.query(LearningSessionModel)
            .filter(
                LearningSessionModel.id == session_id,
                LearningSessionModel.status == "active",
            )
            .first()
        )
        if not session_obj:
            raise PermissionError("Active learning session required.")

        # 2. Look up question
        q = (
            db.query(Question)
            .filter((Question.id == question_identifier) | (Question.code == question_identifier))
            .first()
        )
        if not q:
            raise ValueError(f"Question '{question_identifier}' not found.")

        # 3. Deterministic educational diagnosis
        diag_result = classify_reasoning(
            question_id=q.code or q.id,
            student_answer=student_answer,
            reasoning_text=reasoning_text or "",
        )

        # 4. Locate or create a practice attempt for this session
        practice_assess = (
            db.query(Assessment)
            .filter(
                (Assessment.code == "FRACTIONS_PRACTICE")
                | (Assessment.assessment_type == "practice")
            )
            .first()
        )
        if not practice_assess:
            # Fallback to any active assessment
            practice_assess = db.query(Assessment).first()

        practice_attempt = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.session_id == session_id,
                AssessmentAttempt.assessment_id == practice_assess.id,
                AssessmentAttempt.status == "in_progress",
            )
            .first()
        )
        if not practice_attempt:
            practice_attempt = AssessmentAttempt(
                session_id=session_id,
                assessment_id=practice_assess.id,
                attempt_no=1,
                status="in_progress",
                started_at=utc_now(),
            )
            db.add(practice_attempt)
            db.flush()

        # 5. Record or update AnswerSubmission
        sub = (
            db.query(AnswerSubmission)
            .filter(
                AnswerSubmission.attempt_id == practice_attempt.id,
                AnswerSubmission.question_id == q.id,
            )
            .first()
        )
        # Find matching option if available
        matched_opt = None
        for opt in q.options:
            if (
                opt.option_key.upper() == student_answer.strip().upper()
                or opt.id == student_answer.strip()
            ):
                matched_opt = opt
                break

        if not sub:
            sub = AnswerSubmission(
                attempt_id=practice_attempt.id,
                question_id=q.id,
                selected_option_id=matched_opt.id if matched_opt else None,
                answer_text=student_answer,
                is_correct=diag_result.is_correct,
                points_awarded=1.0 if diag_result.is_correct else 0.0,
                submitted_at=utc_now(),
            )
            db.add(sub)
            db.flush()
        else:
            sub.answer_text = student_answer
            if matched_opt:
                sub.selected_option_id = matched_opt.id
            sub.is_correct = diag_result.is_correct
            sub.points_awarded = 1.0 if diag_result.is_correct else 0.0
            sub.submitted_at = utc_now()
            db.flush()

        # 6. Record reasoning response if provided
        if reasoning_text and reasoning_text.strip():
            max_seq = (
                db.query(func.max(ReasoningResponse.sequence_no))
                .filter(ReasoningResponse.answer_submission_id == sub.id)
                .scalar()
            )
            r_seq = (max_seq or 0) + 1
            reasoning = ReasoningResponse(
                answer_submission_id=sub.id,
                sequence_no=r_seq,
                response_text=reasoning_text.strip(),
                input_mode=input_mode,
                created_at=utc_now(),
            )
            db.add(reasoning)

        # 7. Record/Update Misconception Hypothesis
        concept_id = None
        if q.concepts:
            concept_id = q.concepts[0].concept_id

        if diag_result.diagnosis_code.value in ("M1", "M2", "M3", "M4", "S1"):
            existing_hyp = (
                db.query(MisconceptionHypothesis)
                .filter(
                    MisconceptionHypothesis.session_id == session_id,
                    MisconceptionHypothesis.code == diag_result.diagnosis_code.value,
                    MisconceptionHypothesis.status.in_(["tentative", "confirmed"]),
                )
                .first()
            )
            if existing_hyp:
                existing_hyp.evidence_answer_id = sub.id
                existing_hyp.description = diag_result.student_feedback
                existing_hyp.updated_at = utc_now()
            else:
                new_hyp = MisconceptionHypothesis(
                    session_id=session_id,
                    concept_id=concept_id,
                    evidence_answer_id=sub.id,
                    code=diag_result.diagnosis_code.value,
                    description=diag_result.student_feedback,
                    confidence=0.9 if diag_result.certainty.value == "high" else 0.7,
                    status="tentative",
                    created_at=utc_now(),
                    updated_at=utc_now(),
                )
                db.add(new_hyp)
        elif diag_result.diagnosis_code.value == "NONE" and diag_result.is_correct:
            # Check if there is an active tentative hypothesis for this concept and resolve it
            if concept_id:
                active_hyp = (
                    db.query(MisconceptionHypothesis)
                    .filter(
                        MisconceptionHypothesis.session_id == session_id,
                        MisconceptionHypothesis.concept_id == concept_id,
                        MisconceptionHypothesis.status == "tentative",
                    )
                    .first()
                )
                if active_hyp:
                    active_hyp.status = "resolved"
                    active_hyp.updated_at = utc_now()

        # 8. Log Tutoring Interactions
        cur_seq = TutoringService._get_next_interaction_sequence(db, session_id)
        # Student message
        student_content = f"Answer: {student_answer}"
        if reasoning_text and reasoning_text.strip():
            student_content += f". Reasoning: {reasoning_text.strip()}"
        student_int = TutoringInteraction(
            session_id=session_id,
            sequence_no=cur_seq,
            role="student",
            interaction_type="reasoning_response" if reasoning_text else "question",
            content=student_content,
            created_at=utc_now(),
        )
        db.add(student_int)

        # Tutor feedback message
        tutor_content = diag_result.student_feedback
        if diag_result.clarifying_question:
            tutor_content += f"\n\n{diag_result.clarifying_question}"
        tutor_int = TutoringInteraction(
            session_id=session_id,
            sequence_no=cur_seq + 1,
            role="tutor",
            interaction_type="practice_feedback",
            content=tutor_content,
            created_at=utc_now(),
        )
        db.add(tutor_int)

        # Update session stage to practice if in pre_assessment
        if session_obj.current_stage in ("initialized", "pre_assessment", "WELCOME"):
            session_obj.current_stage = "practice"
            session_obj.updated_at = utc_now()

        db.flush()

        res_dict = diag_result.model_dump()
        res_dict["answer_submission_id"] = sub.id
        res_dict["tutor_prompt"] = tutor_content
        return res_dict

    @staticmethod
    def evaluate_teachback(
        db: Session,
        session_id: str,
        explanation: str,
        input_mode: str = "text",
    ) -> Dict[str, Any]:
        """Evaluate a student teach-back explanation using the multi-criteria rubric and record interactions."""
        # 1. Verify session is active
        session_obj = (
            db.query(LearningSessionModel)
            .filter(
                LearningSessionModel.id == session_id,
                LearningSessionModel.status == "active",
            )
            .first()
        )
        if not session_obj:
            raise PermissionError("Active learning session required.")

        # 2. Run deterministic rubric evaluation
        evaluation = evaluate_teachback_text(explanation)

        # 3. Log Tutoring Interactions
        cur_seq = TutoringService._get_next_interaction_sequence(db, session_id)
        student_int = TutoringInteraction(
            session_id=session_id,
            sequence_no=cur_seq,
            role="student",
            interaction_type="teach_back",
            content=explanation.strip(),
            created_at=utc_now(),
        )
        db.add(student_int)

        tutor_int = TutoringInteraction(
            session_id=session_id,
            sequence_no=cur_seq + 1,
            role="tutor",
            interaction_type="feedback",
            content=evaluation.overall_feedback,
            created_at=utc_now(),
        )
        db.add(tutor_int)

        # 4. Advance stage to teach_back if currently in practice
        if session_obj.current_stage == "practice":
            session_obj.current_stage = "teach_back"
            session_obj.updated_at = utc_now()

        db.flush()

        return evaluation.model_dump()

    @staticmethod
    def get_history(db: Session, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve ordered conversation & tutoring interactions for the authenticated session."""
        interactions = (
            db.query(TutoringInteraction)
            .filter(TutoringInteraction.session_id == session_id)
            .order_by(TutoringInteraction.sequence_no.asc())
            .all()
        )
        return [
            {
                "id": item.id,
                "sequence_no": item.sequence_no,
                "role": item.role,
                "interaction_type": item.interaction_type,
                "content": item.content,
                "created_at": item.created_at.isoformat(),
            }
            for item in interactions
        ]

    @staticmethod
    def get_misconceptions(db: Session, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve active misconception hypotheses for the authenticated session."""
        hypotheses = (
            db.query(MisconceptionHypothesis)
            .filter(MisconceptionHypothesis.session_id == session_id)
            .order_by(MisconceptionHypothesis.created_at.asc())
            .all()
        )
        results = []
        for h in hypotheses:
            concept_code = None
            if h.concept:
                concept_code = h.concept.code
            results.append(
                {
                    "id": h.id,
                    "code": h.code,
                    "concept_code": concept_code,
                    "description": h.description,
                    "confidence": h.confidence,
                    "status": h.status,
                    "evidence_answer_id": h.evidence_answer_id,
                    "created_at": h.created_at.isoformat(),
                    "updated_at": h.updated_at.isoformat() if h.updated_at else None,
                }
            )
        return results
