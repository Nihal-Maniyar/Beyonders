"""Reusable Streamlit UI components for LearnLoop AI."""

import html
from typing import List

import streamlit as st

from learnloop.domain.mastery_rules import MasteryStatus
from learnloop.schemas.assessment import PrePostReport
from learnloop.schemas.teachback import CriterionResult, CriterionStatus


def render_fraction_strips(fraction_a: str = "2/3", fraction_b: str = "2/5") -> None:
    """Render side-by-side fraction strips comparing two fractions."""
    # Strip 1: 2/3 (3 segments, 2 shaded)
    # Strip 2: 2/5 (5 segments, 2 shaded)
    html_content = f"""
    <div class="fraction-strip-container">
        <div class="strip-label">Whole Unit Strip 1: {fraction_a} (3 equal parts, 2 shaded = 66.7% of whole)</div>
        <div class="strip-bar">
            <div class="strip-segment segment-shaded" style="width: 33.33%;">1/3</div>
            <div class="strip-segment segment-shaded" style="width: 33.33%;">1/3</div>
            <div class="strip-segment segment-unshaded" style="width: 33.34%;">1/3</div>
        </div>

        <div class="strip-label">Whole Unit Strip 2: {fraction_b} (5 equal parts, 2 shaded = 40.0% of whole)</div>
        <div class="strip-bar">
            <div class="strip-segment segment-shaded" style="width: 20%;">1/5</div>
            <div class="strip-segment segment-shaded" style="width: 20%;">1/5</div>
            <div class="strip-segment segment-unshaded" style="width: 20%;">1/5</div>
            <div class="strip-segment segment-unshaded" style="width: 20%;">1/5</div>
            <div class="strip-segment segment-unshaded" style="width: 20%;">1/5</div>
        </div>
        <div style="font-size: 0.85rem; color: #167D78; font-weight: 600; margin-top: 0.5rem;">
            Notice: Each 1/3 slice is significantly wider than each 1/5 slice because the whole was cut into fewer pieces!
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def render_rubric_results(criterion_results: List[CriterionResult]) -> None:
    """Render rubric evaluation criteria status and evidence."""
    badge_classes = {
        CriterionStatus.DEMONSTRATED: "badge-teal",
        CriterionStatus.PARTIAL: "badge-amber",
        CriterionStatus.INCORRECT: "badge-red",
        CriterionStatus.NOT_DEMONSTRATED: "badge-slate",
    }
    status_labels = {
        CriterionStatus.DEMONSTRATED: "Demonstrated",
        CriterionStatus.PARTIAL: "Partially Demonstrated",
        CriterionStatus.INCORRECT: "Misconception / Incorrect",
        CriterionStatus.NOT_DEMONSTRATED: "Not Yet Demonstrated",
    }

    st.markdown("### 📋 Teach-Back Rubric Evaluation")
    for res in criterion_results:
        badge_cls = badge_classes.get(res.status, "badge-slate")
        label = status_labels.get(res.status, res.status.value)
        safe_evidence = html.escape(res.evidence)
        card_html = f"""
        <div class="notebook-card" style="margin-bottom: 0.5rem; padding: 0.8rem 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <strong style="font-size: 0.95rem; color: #172A3A;">Criterion {res.criterion_id}</strong>
                <span class="badge {badge_cls}">{label}</span>
            </div>
            <div style="font-size: 0.88rem; color: #434F57;">
                <strong>Grounded Evidence:</strong> {safe_evidence}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


def render_pre_post_summary(report: PrePostReport) -> None:
    """Render the pre/post score change, paired n, and limitations."""
    sign = "+" if report.score_change_pp > 0 else ""
    st.markdown(
        f"""
        <div class="notebook-card card-teal">
            <h3 style="margin-top: 0; color: #167D78;">📊 Pre- vs Post-Assessment Outcome</h3>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.85rem; color: #687782;">PRE-ASSESSMENT</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #172A3A;">{report.pre_correct}/{report.pre_total} ({report.pre_percent}%)</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: #687782;">POST-ASSESSMENT</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #172A3A;">{report.post_correct}/{report.post_total} ({report.post_percent}%)</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: #687782;">OBSERVED SCORE CHANGE</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #167D78;">{sign}{report.score_change_pp} pp</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: #687782;">PAIRED SAMPLE SIZE</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #172A3A;">n = {report.paired_sample_count}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Concept-Level Breakdown")
    col1, col2, col3 = st.columns(3)
    cols = {"C1": col1, "C2": col2, "C3": col3}
    titles = {
        "C1": "C1: Understanding Fractions",
        "C2": "C2: Comparing Fractions",
        "C3": "C3: Equivalent Fractions",
    }
    for cid, cscore in report.concept_breakdown.items():
        if cid in cols:
            with cols[cid]:
                csign = "+" if cscore.change_pp > 0 else ""
                st.metric(
                    label=titles.get(cid, cid),
                    value=f"{cscore.post_correct}/{cscore.post_total} ({cscore.post_percent}%)",
                    delta=f"{csign}{cscore.change_pp} pp (from {cscore.pre_percent}%)",
                )

    with st.expander("⚠️ Evaluation Limitations & Methodology Disclosure", expanded=True):
        st.markdown(
            """
            * **Practice Effect**: Reusing identical assessment items can introduce a familiarization effect.
            * **Sample Size**: A single student comparison (n=1) does not scientifically isolate the AI tutor as the sole cause of improvement.
            * **Assessment Scope**: The 6 fixed items represent a focused diagnostic check for comparing fractions, not long-term retention.
            * **Transfer**: Transfer was evaluated with an additional distinct transfer item during practice.
            """
        )


def render_mastery_badge(status: MasteryStatus) -> str:
    badges = {
        MasteryStatus.NOT_ASSESSED: '<span class="badge badge-slate">Not Assessed</span>',
        MasteryStatus.DEVELOPING: '<span class="badge badge-amber">Developing</span>',
        MasteryStatus.PRACTISING: '<span class="badge badge-teal">Practising</span>',
        MasteryStatus.MASTERED: '<span class="badge badge-teal" style="background:#167D78; color:#FFF;">Mastered ★</span>',
    }
    return badges.get(status, '<span class="badge badge-slate">Unknown</span>')
