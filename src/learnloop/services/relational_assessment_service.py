"""Relational Assessment Service implementing context.md Sections 16–22.

Orchestrates safe assessment content delivery, attempt lifecycle, answer validation,
transactional scoring, and derived progress reporting across the 15 relational entities.
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from learnloop.db.models import (
    AnswerSubmission,
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    MisconceptionHypothesis,
    QuestionOption,
    utc_now,
)


class RelationalAssessmentService:
    @staticmethod
    def get_safe_assessment(db: Session, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve assessment definition with ordered questions and options.

        Guarantees that is_correct and internal explanations are NEVER leaked to the client.
        """
        assessment = (
            db.query(Assessment)
            .filter(Assessment.code == code, Assessment.is_active.is_(True))
            .order_by(Assessment.version.desc())
            .first()
        )
        if not assessment:
            return None

        questions_payload = []
        for aq in assessment.questions:
            q = aq.question
            if not q or q.status != "published":
                continue

            options_payload = [
                {
                    "id": opt.id,
                    "option_key": opt.option_key,
                    "option_text": opt.option_text,
                }
                for opt in sorted(q.options, key=lambda o: o.option_key)
            ]

            questions_payload.append(
                {
                    "id": q.id,
                    "code": q.code,
                    "position": aq.position,
                    "prompt": q.prompt,
                    "question_type": q.question_type,
                    "points_possible": aq.points_possible,
                    "options": options_payload,
                }
            )

        return {
            "id": assessment.id,
            "code": assessment.code,
            "title": assessment.title,
            "assessment_type": assessment.assessment_type,
            "version": assessment.version,
            "questions": questions_payload,
        }

    @staticmethod
    def start_attempt(db: Session, session_id: str, assessment_code: str) -> AssessmentAttempt:
        """Start a new assessment attempt for the active session atomically."""
        assessment = (
            db.query(Assessment)
            .filter(Assessment.code == assessment_code, Assessment.is_active.is_(True))
            .order_by(Assessment.version.desc())
            .first()
        )
        if not assessment:
            raise ValueError(f"Assessment '{assessment_code}' not found or inactive.")

        # Compute next attempt_no atomically for this session & assessment
        latest_attempt = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.session_id == session_id,
                AssessmentAttempt.assessment_id == assessment.id,
            )
            .order_by(AssessmentAttempt.attempt_no.desc())
            .first()
        )
        next_attempt_no = (latest_attempt.attempt_no + 1) if latest_attempt else 1

        attempt = AssessmentAttempt(
            session_id=session_id,
            assessment_id=assessment.id,
            attempt_no=next_attempt_no,
            status="in_progress",
        )
        db.add(attempt)
        db.flush()
        return attempt

    @staticmethod
    def get_attempt(db: Session, attempt_id: str, session_id: str) -> Optional[AssessmentAttempt]:
        """Fetch attempt status verifying strict session ownership."""
        return (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.session_id == session_id,
            )
            .first()
        )

    @staticmethod
    def submit_answer(
        db: Session,
        attempt_id: str,
        session_id: str,
        question_id: str,
        selected_option_id: Optional[str] = None,
        answer_text: Optional[str] = None,
    ) -> AnswerSubmission:
        """Record an answer submission with strict membership validation.

        - Verifies attempt session ownership and active status.
        - Verifies question belongs to this assessment version.
        - Verifies selected option belongs to the question.
        - Computes correctness server-side.
        - Executes idempotently.
        """
        attempt = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.session_id == session_id,
            )
            .first()
        )
        if not attempt:
            raise PermissionError("Attempt not found or unauthorized.")

        if attempt.status != "in_progress":
            raise ValueError("Cannot submit answers to a completed or abandoned attempt.")

        # Check question membership in assessment
        aq = (
            db.query(AssessmentQuestion)
            .filter(
                AssessmentQuestion.assessment_id == attempt.assessment_id,
                AssessmentQuestion.question_id == question_id,
            )
            .first()
        )
        if not aq:
            raise ValueError("Question does not belong to this assessment.")

        is_correct = False
        points_awarded = 0.0

        if selected_option_id:
            option = (
                db.query(QuestionOption)
                .filter(
                    QuestionOption.id == selected_option_id,
                    QuestionOption.question_id == question_id,
                )
                .first()
            )
            if not option:
                raise ValueError("Selected option does not belong to this question.")

            is_correct = option.is_correct
            points_awarded = aq.points_possible if is_correct else 0.0

        # Idempotent upsert
        submission = (
            db.query(AnswerSubmission)
            .filter(
                AnswerSubmission.attempt_id == attempt_id,
                AnswerSubmission.question_id == question_id,
            )
            .first()
        )

        if submission:
            submission.selected_option_id = selected_option_id
            submission.answer_text = answer_text
            submission.is_correct = is_correct
            submission.points_awarded = points_awarded
            submission.submitted_at = utc_now()
        else:
            submission = AnswerSubmission(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                answer_text=answer_text,
                is_correct=is_correct,
                points_awarded=points_awarded,
            )
            db.add(submission)

        db.flush()
        return submission

    @staticmethod
    def complete_attempt(db: Session, attempt_id: str, session_id: str) -> AssessmentAttempt:
        """Complete an attempt atomically, computing score server-side.

        Idempotent: if already completed, returns existing completed attempt without mutating.
        """
        attempt = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.session_id == session_id,
            )
            .first()
        )
        if not attempt:
            raise PermissionError("Attempt not found or unauthorized.")

        if attempt.status == "completed":
            return attempt

        # Validate required questions
        assigned_questions = (
            db.query(AssessmentQuestion)
            .filter(AssessmentQuestion.assessment_id == attempt.assessment_id)
            .all()
        )
        assigned_q_ids = {aq.question_id for aq in assigned_questions}

        submissions = (
            db.query(AnswerSubmission).filter(AnswerSubmission.attempt_id == attempt_id).all()
        )
        answered_q_ids = {sub.question_id for sub in submissions}

        missing = assigned_q_ids - answered_q_ids
        if missing:
            raise ValueError(
                f"Attempt has unanswered required questions ({len(missing)} remaining)."
            )

        # Calculate final score transactionally
        raw_score = sum(s.points_awarded or 0.0 for s in submissions)
        max_score = sum(aq.points_possible for aq in assigned_questions)

        attempt.raw_score = round(raw_score, 2)
        attempt.max_score = round(max_score, 2)
        attempt.status = "completed"
        attempt.completed_at = utc_now()

        db.flush()
        return attempt

    @staticmethod
    def get_progress(db: Session, session_id: str) -> Dict[str, Any]:
        """Compute progress summary, pre/post comparison, and misconception history."""
        # Find completed pre and post attempts
        pre_assess = db.query(Assessment).filter(Assessment.assessment_type == "pre").first()
        post_assess = db.query(Assessment).filter(Assessment.assessment_type == "post").first()

        pre_attempt = None
        if pre_assess:
            pre_attempt = (
                db.query(AssessmentAttempt)
                .filter(
                    AssessmentAttempt.session_id == session_id,
                    AssessmentAttempt.assessment_id == pre_assess.id,
                    AssessmentAttempt.status == "completed",
                )
                .order_by(AssessmentAttempt.completed_at.desc())
                .first()
            )

        post_attempt = None
        if post_assess:
            post_attempt = (
                db.query(AssessmentAttempt)
                .filter(
                    AssessmentAttempt.session_id == session_id,
                    AssessmentAttempt.assessment_id == post_assess.id,
                    AssessmentAttempt.status == "completed",
                )
                .order_by(AssessmentAttempt.completed_at.desc())
                .first()
            )

        pre_pct = (
            round((pre_attempt.raw_score / pre_attempt.max_score) * 100.0, 1)
            if pre_attempt and pre_attempt.max_score
            else None
        )
        post_pct = (
            round((post_attempt.raw_score / post_attempt.max_score) * 100.0, 1)
            if post_attempt and post_attempt.max_score
            else None
        )

        change_pp = (
            round(post_pct - pre_pct, 1) if pre_pct is not None and post_pct is not None else None
        )

        # Misconceptions summary
        hypotheses = (
            db.query(MisconceptionHypothesis)
            .filter(MisconceptionHypothesis.session_id == session_id)
            .order_by(MisconceptionHypothesis.created_at.desc())
            .all()
        )

        misconceptions_summary = [
            {
                "code": h.code,
                "description": h.description,
                "confidence": h.confidence,
                "status": h.status,
            }
            for h in hypotheses
        ]

        return {
            "pre_assessment": {
                "completed": pre_attempt is not None,
                "raw_score": pre_attempt.raw_score if pre_attempt else None,
                "max_score": pre_attempt.max_score if pre_attempt else None,
                "percent": pre_pct,
            },
            "post_assessment": {
                "completed": post_attempt is not None,
                "raw_score": post_attempt.raw_score if post_attempt else None,
                "max_score": post_attempt.max_score if post_attempt else None,
                "percent": post_pct,
            },
            "comparison": {
                "is_comparable": change_pp is not None,
                "percentage_point_change": change_pp,
                "status_message": (
                    f"Growth of {change_pp:+.1f} percentage points."
                    if change_pp is not None
                    else "Complete both pre- and post-assessments to view comparison."
                ),
            },
            "misconceptions": misconceptions_summary,
        }
