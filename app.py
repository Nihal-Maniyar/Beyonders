"""LearnLoop AI — The Learning Notebook
Adaptive AI Tutor & Misconception Detector for Comparing Fractions (VORTEXA 3.0, E-01).
"""

import sys
from pathlib import Path

# Ensure src is in sys.path so learnloop is always importable
src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import streamlit as st

from learnloop.content.loader import get_content_bank
from learnloop.db.session import get_db_session, init_db
from learnloop.domain.mastery_rules import MasteryStatus
from learnloop.repositories.attempts import AttemptRepository
from learnloop.repositories.learners import LearnerRepository
from learnloop.services.assessment_service import AssessmentService
from learnloop.services.diagnosis_service import DiagnosisService
from learnloop.services.mastery_service import MasteryService
from learnloop.services.review_service import ReviewService
from learnloop.services.teachback_service import TeachBackService
from learnloop.services.tutor_service import TutorService
from learnloop.ui.components import (
    render_fraction_strips,
    render_mastery_badge,
    render_pre_post_summary,
    render_rubric_results,
)
from learnloop.ui.theme import NOTEBOOK_CSS

# Page configuration
st.set_page_config(
    page_title="LearnLoop AI — The Learning Notebook",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply editorial learning notebook CSS
st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)

# Ensure database tables are created
init_db()

# Load verified content bank
content_bank = get_content_bank()
tutor_service = TutorService(content_bank)

# Session State Initialization
if "learner_id" not in st.session_state:
    st.session_state.learner_id = "demo_student_01"
if "display_name" not in st.session_state:
    st.session_state.display_name = "Alex Morgan"
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "WELCOME"
if "pre_index" not in st.session_state:
    st.session_state.pre_index = 0
if "pre_run_id" not in st.session_state:
    st.session_state.pre_run_id = None
if "post_index" not in st.session_state:
    st.session_state.post_index = 0
if "post_run_id" not in st.session_state:
    st.session_state.post_run_id = None
if "active_concept_id" not in st.session_state:
    st.session_state.active_concept_id = "C1"
if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None
if "last_teachback_eval" not in st.session_state:
    st.session_state.last_teachback_eval = None
if "unlocked_stages" not in st.session_state:
    st.session_state.unlocked_stages = {"WELCOME"}


def unlock_stage(stage: str):
    st.session_state.unlocked_stages.add(stage)


def navigate_to(stage: str):
    unlock_stage(stage)
    st.session_state.current_stage = stage
    st.rerun()


# --- SIDEBAR: Learner Profile & Notebook Navigator ---
with st.sidebar:
    st.markdown("### 📓 Notebook Profile")
    st.markdown(
        f"""
        <div style="background:#FFF; padding:0.8rem 1rem; border-radius:6px; border:1px solid #E2DDD3; margin-bottom:1rem;">
            <div style="font-size:0.8rem; color:#687782; font-weight:600;">ACTIVE LEARNER</div>
            <div style="font-size:1.1rem; font-weight:700; color:#172A3A;">{st.session_state.display_name}</div>
            <div style="font-size:0.75rem; color:#687782;">ID: {st.session_state.learner_id}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧭 Learning Journey")
    stages_order = [
        ("WELCOME", "1. Chapter Overview"),
        ("PRE_ASSESSMENT", "2. Baseline Pre-Assessment"),
        ("LESSON", "3. Concept Lessons"),
        ("PRACTICE", "4. Practice & Diagnosis"),
        ("TEACH_BACK", "5. Student Teach-Back"),
        ("TEACH_BACK_FEEDBACK", "6. Rubric Evaluation"),
        ("POST_ASSESSMENT", "7. Final Post-Assessment"),
        ("PROGRESS_REPORT", "8. Mastery & Progress"),
    ]

    for stage_key, stage_label in stages_order:
        is_current = st.session_state.current_stage == stage_key
        is_unlocked = stage_key in st.session_state.unlocked_stages

        btn_label = f"👉 {stage_label}" if is_current else stage_label
        if st.button(
            btn_label,
            key=f"nav_{stage_key}",
            disabled=not is_unlocked,
            use_container_width=True,
        ):
            navigate_to(stage_key)

    st.divider()
    if st.button("🔄 Reset Demo Session", use_container_width=True):
        st.session_state.pre_index = 0
        st.session_state.pre_run_id = None
        st.session_state.post_index = 0
        st.session_state.post_run_id = None
        st.session_state.last_diagnosis = None
        st.session_state.last_teachback_eval = None
        st.session_state.unlocked_stages = {"WELCOME"}
        navigate_to("WELCOME")


# ==========================================
# SCREEN 1: WELCOME & SYLLABUS OVERVIEW
# ==========================================
if st.session_state.current_stage == "WELCOME":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>LearnLoop AI — The Learning Notebook</h1>
            <p>Adaptive AI Tutor & Misconception Detector · Comparing Fractions (Grade 4–6)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### Welcome to Your Fractions Study Notebook!
        LearnLoop AI does not simply mark answers right or wrong. It investigates **how you reason**,
        identifies possible misconceptions, adapts explanations, evaluates your teach-back against an explicit rubric,
        and tracks your mastery over time.
        """
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("#### 📚 Approved Chapter Syllabus: Comparing Fractions")
        concepts = tutor_service.get_all_concepts()
        for c in concepts:
            with st.expander(f"📌 {c.concept_id}: {c.title}", expanded=True):
                st.markdown(f"**Core Principle:** {c.verified_explanation}")
                st.markdown("**Learning Objectives:**")
                for obj in c.learning_objectives:
                    st.markdown(f"- {obj}")

        st.markdown(
            """
            <div class="notebook-card card-teal" style="margin-top:1rem;">
                <strong>👩‍🏫 Teacher Oversight & Curriculum Alignment:</strong><br>
                <span style="font-size:0.9rem; color:#434F57;">
                LearnLoop AI is an educational aid that supports teachers rather than replacing them.
                All curriculum explanations, question items, and rubric standards are human-verified
                and grounded in Common Core and NCTM standards.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("#### 🚀 Ready to Begin?")
        st.markdown(
            """
            Before we teach, we take a **6-question baseline pre-assessment** (2 questions per concept).
            This helps the tutor understand what you already know and where you might need guidance.
            """
        )

        name_input = st.text_input(
            "Student Name:", value=st.session_state.display_name, key="input_student_name"
        )
        if name_input != st.session_state.display_name:
            st.session_state.display_name = name_input

        if st.button("Start Baseline Assessment ➔", type="primary", use_container_width=True):
            with get_db_session() as db:
                learner_repo = LearnerRepository(db)
                learner_repo.get_or_create(
                    st.session_state.learner_id,
                    display_name=st.session_state.display_name,
                    is_demo=True,
                )
                session_obj = learner_repo.create_learning_session(
                    st.session_state.learner_id,
                    chapter_id=content_bank.chapter.chapter_id,
                    content_version=content_bank.chapter.content_version,
                )
                st.session_state.session_id = session_obj.id

                assess_service = AssessmentService(db, content_bank)
                run = assess_service.start_pre_assessment(
                    st.session_state.learner_id, session_id=session_obj.id
                )
                st.session_state.pre_run_id = run.id

            st.session_state.pre_index = 0
            navigate_to("PRE_ASSESSMENT")


# ==========================================
# SCREEN 2: PRE-ASSESSMENT
# ==========================================
elif st.session_state.current_stage == "PRE_ASSESSMENT":
    questions = content_bank.get_fixed_assessment_questions()
    total_q = len(questions)
    curr_idx = st.session_state.pre_index

    if curr_idx >= total_q:
        navigate_to("LESSON")

    q = questions[curr_idx]
    concept = content_bank.get_concept(q.concept_id)

    st.markdown(
        f"""
        <div class="notebook-header">
            <h1>Baseline Pre-Assessment (Question {curr_idx + 1} of {total_q})</h1>
            <p>Concept: {concept.title if concept else q.concept_id} · Answer each question to the best of your ability</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress((curr_idx) / total_q)

    st.markdown(
        f"""
        <div class="notebook-card" style="font-size:1.15rem; font-weight:600; color:#172A3A;">
            {q.question_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_option = st.radio(
        "Select your answer:",
        options=q.options,
        key=f"pre_q_radio_{q.question_id}_{curr_idx}",
    )

    st.markdown(
        "<div style='font-size:0.85rem; color:#687782;'>Note: Answers and explanations are kept confidential during pre-assessment to measure your baseline accurately.</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        btn_label = "Save & Next ➔" if curr_idx < total_q - 1 else "Finish Pre-Assessment ➔"
        if st.button(btn_label, type="primary", use_container_width=True):
            # Extract choice letter (e.g. "A" from "A) ...")
            choice = selected_option[0] if selected_option else ""

            with get_db_session() as db:
                assess_service = AssessmentService(db, content_bank)
                # Ensure run exists
                if not st.session_state.pre_run_id:
                    run = assess_service.start_pre_assessment(
                        st.session_state.learner_id, session_id=st.session_state.session_id
                    )
                    st.session_state.pre_run_id = run.id

                assess_service.record_answer(
                    run_id=st.session_state.pre_run_id,
                    question_id=q.question_id,
                    student_answer=choice,
                )

                if curr_idx >= total_q - 1:
                    assess_service.complete_run(st.session_state.pre_run_id)

            if curr_idx < total_q - 1:
                st.session_state.pre_index += 1
                st.rerun()
            else:
                navigate_to("LESSON")


# ==========================================
# SCREEN 3: CONCEPT LESSON
# ==========================================
elif st.session_state.current_stage == "LESSON":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>Interactive Concept Lessons</h1>
            <p>Study the approved principles, analogies, and worked examples</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    concept_tab_labels = [
        "C1: Understanding Fractions",
        "C2: Comparing Fractions",
        "C3: Equivalent Fractions",
    ]
    tab1, tab2, tab3 = st.tabs(concept_tab_labels)
    tabs = {"C1": tab1, "C2": tab2, "C3": tab3}

    for cid, tab in tabs.items():
        concept = content_bank.get_concept(cid)
        if not concept:
            continue

        with tab:
            st.markdown(f"### {concept.title}")
            st.markdown(
                f"""
                <div class="notebook-card card-teal">
                    <strong>💡 Core Definition:</strong><br>{concept.verified_explanation}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"**🍕 Intuitive Analogy:** {concept.intuitive_analogy}")

            # Visual fraction strip for C2
            if cid == "C2":
                st.markdown("#### 📏 Visual Model: Fractions Strips (2/3 vs 2/5)")
                render_fraction_strips("2/3", "2/5")

            st.markdown("#### 📝 Step-by-Step Worked Example")
            for we in concept.worked_examples:
                st.markdown(f"**Problem:** *{we.prompt}*")
                for step in we.steps:
                    st.markdown(f"- {step}")

            if concept.common_mistakes:
                st.markdown("#### ⚠️ Common Pitfalls to Avoid:")
                for cm in concept.common_mistakes:
                    st.markdown(f"- {cm}")

    st.divider()
    st.markdown("### Ready to Test Your Understanding?")
    st.markdown("Try answering practice questions where you explain your reasoning to the tutor.")
    if st.button("Proceed to Practice & Diagnostic Quiz ➔", type="primary"):
        navigate_to("PRACTICE")


# ==========================================
# SCREEN 4: PRACTICE & DIAGNOSTIC CONVERSATION
# ==========================================
elif st.session_state.current_stage == "PRACTICE":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>Practice Quiz & Reasoning Diagnosis</h1>
            <p>Explain your thinking — the tutor investigates reasoning behind each answer</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    practice_questions = [
        content_bank.get_question("Q_C2_PRE_01"),  # Canonical: 2/5 vs 2/3
        content_bank.get_question("Q_C2_PRAC_01"),  # Practice: 3/7 vs 3/5
        content_bank.get_question("Q_C3_PRE_02"),  # Equivalence: Adding 2 to 1/3
        content_bank.get_question("Q_C2_TRANSFER_01"),  # Transfer: 3/7 vs 4/9
    ]
    practice_questions = [q for q in practice_questions if q]

    q_options = {
        q.question_id: f"{q.question_id}: {q.question_text[:60]}..." for q in practice_questions
    }
    selected_qid = st.selectbox(
        "Choose a practice question:",
        options=list(q_options.keys()),
        format_func=lambda x: q_options[x],
        key="practice_select_qid",
    )

    q = content_bank.get_question(selected_qid)
    if q:
        st.markdown(
            f"""
            <div class="notebook-card" style="font-size:1.15rem; font-weight:600; color:#172A3A;">
                {q.question_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        practice_choice = st.radio(
            "Your Answer:", options=q.options, key=f"prac_ans_{q.question_id}"
        )
        practice_reasoning = st.text_area(
            "Explain your reasoning (Why did you choose this answer?):",
            placeholder="e.g. Because thirds are larger pieces than fifths, 2 thirds is bigger than 2 fifths...",
            key=f"prac_reason_{q.question_id}",
        )

        if st.button("Submit Answer & Reasoning ➔", type="primary"):
            choice_letter = practice_choice[0] if practice_choice else ""
            with get_db_session() as db:
                diag_service = DiagnosisService(db, content_bank)
                diag_result = diag_service.diagnose_and_record(
                    learner_id=st.session_state.learner_id,
                    question_id=q.question_id,
                    student_answer=choice_letter,
                    reasoning_text=practice_reasoning,
                    session_id=st.session_state.session_id,
                )
                st.session_state.last_diagnosis = diag_result

        # Display Diagnostic Feedback
        if (
            st.session_state.last_diagnosis
            and st.session_state.last_diagnosis.question_id == q.question_id
        ):
            d = st.session_state.last_diagnosis
            st.divider()

            res_card_class = "card-teal" if d.is_correct else "card-amber"
            status_text = "✅ Correct Answer" if d.is_correct else "❌ Incorrect Answer"
            reason_status_text = f"Reasoning: {d.reasoning_status.value.upper()}"

            st.markdown(
                f"""
                <div class="notebook-card {res_card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <strong>{status_text}</strong>
                        <span class="badge badge-slate">{reason_status_text}</span>
                    </div>
                    <p style="font-size:0.95rem; margin:0.4rem 0;">{d.student_feedback}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Clarification prompt for U1
            if d.clarification_required:
                st.info(f"🤔 **Clarification Request:** {d.clarifying_question}")

            # Remediation activity
            if d.next_activity_id:
                act = content_bank.get_activity(d.next_activity_id)
                if act:
                    with st.expander(f"🛠️ Recommended Activity: {act.title}", expanded=True):
                        st.markdown(f"**Purpose:** {act.purpose}")
                        st.markdown(f"**Instructions:** {act.instructions}")
                        if act.visual_representation:
                            st.code(act.visual_representation)
                        if act.activity_id == "A_FRACTION_STRIPS":
                            render_fraction_strips("2/3", "2/5")

    st.divider()
    st.markdown("### Ready for Student Teach-Back?")
    st.markdown("Explain the concepts in your own words to demonstrate your understanding.")
    if st.button("Continue to Teach-Back Activity ➔"):
        navigate_to("TEACH_BACK")


# ==========================================
# SCREEN 5: TEACH-BACK
# ==========================================
elif st.session_state.current_stage == "TEACH_BACK":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>Student Teach-Back Activity</h1>
            <p>Teach the concepts back in your own words to demonstrate your understanding</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notebook-card card-teal">
            <h4 style="margin-top:0; color:#167D78;">🎙️ Your Teach-Back Prompt:</h4>
            <em>"Explain what you understood about comparing fractions in your own words.
            You can use an example (like pizza slices or fraction strips) to help explain your thinking."</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **Tips for a complete explanation:**
        - What do the numerator and denominator mean?
        - Must the parts be equal in size?
        - How does dividing into more parts affect each part's size?
        - How do you compare fractions?
        - What does it mean for fractions to be equivalent?
        """
    )

    tb_text = st.text_area(
        "Your Explanation:",
        height=200,
        placeholder="Type your explanation here...",
        key="tb_response_input",
    )

    if st.button("Submit Explanation for Rubric Evaluation ➔", type="primary"):
        if not tb_text.strip():
            st.warning("Please enter your explanation before submitting.")
        else:
            with get_db_session() as db:
                tb_service = TeachBackService(db, content_bank)
                evaluation = tb_service.submit_and_evaluate(
                    learner_id=st.session_state.learner_id,
                    explanation=tb_text,
                    input_source="typed",
                    session_id=st.session_state.session_id,
                )
                st.session_state.last_teachback_eval = evaluation

            navigate_to("TEACH_BACK_FEEDBACK")


# ==========================================
# SCREEN 6: TEACH-BACK FEEDBACK & REVISION
# ==========================================
elif st.session_state.current_stage == "TEACH_BACK_FEEDBACK":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>Teach-Back Evaluation & Rubric Feedback</h1>
            <p>Objective rubric-grounded assessment of your explanation</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    evaluation = st.session_state.last_teachback_eval
    if not evaluation:
        st.info("No teach-back evaluation recorded yet. Please submit your explanation first.")
        if st.button("Go to Teach-Back"):
            navigate_to("TEACH_BACK")
    else:
        # Score overview
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(
                label="Explanation Rubric Score",
                value=f"{evaluation.coverage_percent}%",
                delta=f"{evaluation.earned_points} / {evaluation.possible_points} points",
            )
        with col2:
            st.markdown(
                f"""
                <div class="notebook-card" style="padding:1rem;">
                    <strong>Overall Feedback:</strong><br>
                    {evaluation.overall_feedback}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Rubric criteria cards
        render_rubric_results(evaluation.criterion_results)

        # Revision advice
        if evaluation.recommended_concepts:
            st.markdown("#### 🎯 Targeted Revision Recommendations:")
            for cid in evaluation.recommended_concepts:
                c = content_bank.get_concept(cid)
                title = c.title if c else cid
                st.warning(
                    f"👉 Review Concept {cid}: **{title}** before taking your final post-assessment."
                )

        col_rev, col_post = st.columns(2)
        with col_rev:
            if st.button("📖 Review Lesson Material", use_container_width=True):
                navigate_to("LESSON")
        with col_post:
            if st.button("Take Final Post-Assessment ➔", type="primary", use_container_width=True):
                with get_db_session() as db:
                    assess_service = AssessmentService(db, content_bank)
                    post_run = assess_service.start_post_assessment(
                        st.session_state.learner_id, session_id=st.session_state.session_id
                    )
                    st.session_state.post_run_id = post_run.id
                st.session_state.post_index = 0
                navigate_to("POST_ASSESSMENT")


# ==========================================
# SCREEN 7: POST-ASSESSMENT & PROGRESS REPORT
# ==========================================
elif st.session_state.current_stage == "POST_ASSESSMENT":
    questions = content_bank.get_fixed_assessment_questions()
    total_q = len(questions)
    curr_idx = st.session_state.post_index

    if curr_idx >= total_q:
        navigate_to("PROGRESS_REPORT")

    q = questions[curr_idx]
    concept = content_bank.get_concept(q.concept_id)

    st.markdown(
        f"""
        <div class="notebook-header">
            <h1>Final Post-Assessment (Question {curr_idx + 1} of {total_q})</h1>
            <p>Concept: {concept.title if concept else q.concept_id} · Measure your understanding after instruction</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(curr_idx / total_q)

    st.markdown(
        f"""
        <div class="notebook-card" style="font-size:1.15rem; font-weight:600; color:#172A3A;">
            {q.question_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    post_choice = st.radio(
        "Select your answer:", options=q.options, key=f"post_q_{q.question_id}_{curr_idx}"
    )

    btn_label = (
        "Save & Next ➔" if curr_idx < total_q - 1 else "Finish Post-Assessment & View Report ➔"
    )
    if st.button(btn_label, type="primary"):
        choice_letter = post_choice[0] if post_choice else ""
        with get_db_session() as db:
            assess_service = AssessmentService(db, content_bank)
            if not st.session_state.post_run_id:
                post_run = assess_service.start_post_assessment(
                    st.session_state.learner_id, session_id=st.session_state.session_id
                )
                st.session_state.post_run_id = post_run.id

            assess_service.record_answer(
                run_id=st.session_state.post_run_id,
                question_id=q.question_id,
                student_answer=choice_letter,
            )

            if curr_idx >= total_q - 1:
                assess_service.complete_run(st.session_state.post_run_id)

        if curr_idx < total_q - 1:
            st.session_state.post_index += 1
            st.rerun()
        else:
            navigate_to("PROGRESS_REPORT")


elif st.session_state.current_stage == "PROGRESS_REPORT":
    st.markdown(
        """
        <div class="notebook-header">
            <h1>Learning Progress & Pre/Post Assessment Report</h1>
            <p>Empirical evidence of score changes, concept mastery, and attempt history</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with get_db_session() as db:
        assess_service = AssessmentService(db, content_bank)
        report = assess_service.get_pre_post_report(st.session_state.learner_id)

        mastery_service = MasteryService(db, content_bank)
        masteries = mastery_service.get_learner_masteries(st.session_state.learner_id)

        review_service = ReviewService(db)
        due_tasks = review_service.get_due_tasks(st.session_state.learner_id)

        attempt_repo = AttemptRepository(db)
        attempts = attempt_repo.get_learner_attempts(st.session_state.learner_id)

    # 1. Pre/Post Comparison
    if report:
        render_pre_post_summary(report)
    else:
        st.info(
            "Pre-assessment and post-assessment must both be completed to generate the comparative report."
        )

    st.divider()

    # 2. Concept Mastery Breakdown
    st.markdown("### 🏆 Demonstrated Concept Mastery")
    st.markdown(
        "<span style='font-size:0.88rem; color:#687782;'>Mastery requires >=4 valid attempts across >=3 distinct items, >=80% weighted accuracy, and passing transfer verification.</span>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    mcols = {"C1": col1, "C2": col2, "C3": col3}
    for cid, mcol in mcols.items():
        summary = masteries.get(cid)
        c = content_bank.get_concept(cid)
        title = c.title if c else cid
        with mcol:
            badge_html = (
                render_mastery_badge(summary.status)
                if summary
                else render_mastery_badge(MasteryStatus.NOT_ASSESSED)
            )
            score_val = summary.score if summary else 0.0
            attempts_val = summary.evidence_attempt_count if summary else 0
            distinct_val = summary.distinct_question_count if summary else 0
            transfer_val = "Passed ✅" if (summary and summary.transfer_passed) else "Pending"

            st.markdown(
                f"""
                <div class="notebook-card" style="padding:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                        <strong>{cid}: {title}</strong>
                    </div>
                    <div style="margin-bottom:0.5rem;">Status: {badge_html}</div>
                    <div style="font-size:0.85rem; color:#434F57;">
                        • Weighted Accuracy: <strong>{score_val}%</strong><br>
                        • Valid Attempts: <strong>{attempts_val}</strong><br>
                        • Distinct Items: <strong>{distinct_val}</strong><br>
                        • Transfer Item: <strong>{transfer_val}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Spaced Review Queue (P2)
    if due_tasks:
        st.markdown("### ⏰ Spaced Review Queue")
        for t in due_tasks:
            st.info(
                f"Task for **{t.concept_id}**: {t.reason} (Due: {t.due_at.strftime('%Y-%m-%d')})"
            )

    # 4. Attempt History Audit
    with st.expander(
        f"📜 Detailed Attempt History ({len(attempts)} attempts logged)", expanded=False
    ):
        if attempts:
            hist_data = [
                {
                    "Question": a.question_id,
                    "Concept": a.concept_id,
                    "Answer": a.response_text,
                    "Correct": "✅" if a.is_correct else "❌",
                    "Reasoning Status": a.reasoning_status,
                    "Diagnosis": a.diagnosis_code or "—",
                    "Activity": a.activity_id or "—",
                    "Timestamp": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if a.created_at
                    else "—",
                }
                for a in attempts
            ]
            st.dataframe(hist_data, use_container_width=True)
        else:
            st.write("No attempts logged yet.")
