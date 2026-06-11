# Autism Risk Screening Application

import os
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from predictor import get_predictor, QCHAT_ITEMS, RESPONSE_OPTIONS

st.set_page_config(
    page_title="Autism Risk Screening",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

#Global styles
# All colours use CSS variables so they adapt to Streamlit light/dark theme.

st.markdown("""
<style>
/* ── tokens ── */
:root {
    --brand:        #4f6ef7;
    --brand-muted:  rgba(79, 110, 247, 0.12);
    --border:       rgba(128, 128, 128, 0.2);
    --radius:       10px;
    --radius-sm:    6px;
}

/* ── stat cards ── */
.stat-card {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1rem;
    text-align: center;
    background: transparent;
}
.stat-number {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--brand);
    line-height: 1.1;
}
.stat-label {
    font-size: 0.8rem;
    margin-top: 0.3rem;
    opacity: 0.65;
}

/* ── step cards ── */
.step-card {
    border-left: 3px solid var(--brand);
    padding: 0.75rem 1rem;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    margin-bottom: 0.6rem;
    background: var(--brand-muted);
}
.step-num {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--brand);
    text-transform: uppercase;
}
.step-text {
    font-size: 0.92rem;
    margin-top: 0.15rem;
    /* inherits Streamlit body colour — safe in dark + light */
}

/* ── data source block ── */
.source-block {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
    background: transparent;
}
.source-title {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--brand);
    margin-bottom: 0.3rem;
}
.source-body {
    font-size: 0.88rem;
    opacity: 0.8;
    line-height: 1.55;
}

/* ── limitation box ── */
.limit-box {
    border: 1px solid rgba(255, 180, 50, 0.4);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    background: rgba(255, 180, 50, 0.07);
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── hero banner ── */
.hero {
    border-left: 4px solid var(--brand);
    padding: 1.2rem 1.4rem;
    border-radius: 0 var(--radius) var(--radius) 0;
    background: var(--brand-muted);
    margin-bottom: 1.6rem;
}
.hero-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--brand);
    margin: 0 0 0.3rem 0;
}
.hero-sub {
    font-size: 0.93rem;
    opacity: 0.75;
    margin: 0;
    line-height: 1.5;
}

/* ── risk meter ── */
.risk-meter-wrap {
    margin: 0.6rem 0 1.2rem;
}
.risk-track {
    height: 10px;
    border-radius: 999px;
    background: var(--border);
    position: relative;
    overflow: hidden;
}
.risk-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* ── fairness table ── */
.stDataFrame { border-radius: var(--radius); overflow: hidden; }

/* ── sidebar tweaks ── */
section[data-testid="stSidebar"] .stCaption { opacity: 0.6; }
</style>
""", unsafe_allow_html=True)


#  Sidebar 
def render_sidebar():
    st.sidebar.header("Child Information")
    age_months = st.sidebar.slider("Age (months)", min_value=18, max_value=36, value=24)
    sex        = st.sidebar.radio("Sex", ["Male", "Female"])

    st.sidebar.divider()
    st.sidebar.header("Contextual Indicators")
    st.sidebar.caption("From the Lesotho DHS 2023–24. Leave unchecked if unknown.")

    stunted      = st.sidebar.checkbox("Child is stunted")
    anaemic      = st.sidebar.checkbox("Child is anaemic")
    no_caregiver = st.sidebar.checkbox("Neither biological parent present in household")
    rural        = st.sidebar.checkbox("Rural residence")

    return age_months, sex, stunted, anaemic, no_caregiver, rural


#  Q-CHAT form 
def render_qchat_form():
    st.subheader("Q-CHAT-10 Responses")
    st.caption("Select the response that best describes the child's typical behaviour.")

    responses = {}
    cols = st.columns(2)
    for i, (item_id, question) in enumerate(QCHAT_ITEMS):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{item_id}.** {question}")
                responses[item_id] = st.selectbox(
                    label=f"Response for {item_id}",
                    options=list(RESPONSE_OPTIONS.keys()),
                    key=f"qchat_{item_id}",
                    label_visibility="collapsed",
                )
    return responses


# Results 
def render_results(result: dict, responses: dict):
    prob    = result["prob_calibrated"]
    at_risk = result["at_risk"]

    st.divider()
    st.subheader("Screening Results")

    if result["demo_mode"]:
        st.warning("Models not loaded. Showing illustrative results only.")

    # Risk banner
    if at_risk:
        st.error("Screening Result: At Risk")
    else:
        st.success("Screening Result: Not At Risk")

    # Metric row
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Probability",   f"{prob:.1%}")
    col2.metric("Decision Threshold", f"{result['threshold']:.2f}")
    col3.metric("Classification",     "At Risk" if at_risk else "Not At Risk")

    st.info(result.get("validation_note", "Model validation details unavailable."))

    # Risk meter
    pct   = int(prob * 100)
    color = "#e74c3c" if at_risk else "#2ecc71"
    st.markdown("**Risk probability**")
    st.markdown(f"""
    <div class="risk-meter-wrap">
        <div class="risk-track">
            <div class="risk-fill" style="width:{pct}%; background:{color};"></div>
        </div>
        <div style="font-size:0.8rem; opacity:0.6; margin-top:4px;">{pct}%</div>
    </div>
    """, unsafe_allow_html=True)

    # SHAP feature contributions
    st.markdown("#### Feature contributions")
    predictor = get_predictor()
    if SHAP_AVAILABLE and predictor.models_loaded:
        try:
            X_beh     = predictor.encode_responses(responses)
            explainer = shap.TreeExplainer(predictor.model_beh)
            shap_vals = explainer.shap_values(X_beh)
            vals      = shap_vals[0] if isinstance(shap_vals, list) else shap_vals[0]
            feat_names = [f"Q{i}" for i in range(1, 11)]

            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_alpha(0)
            ax.set_facecolor("none")
            colours = ["#e74c3c" if v > 0 else "#4f6ef7" for v in vals]
            ax.barh(feat_names, vals, color=colours, height=0.6)
            ax.axvline(0, color="gray", linewidth=0.8, alpha=0.5)
            ax.set_xlabel("SHAP value  (positive = towards At Risk)",
                          color="gray", fontsize=9)
            ax.tick_params(colors="gray", labelsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_title("Feature contribution to this prediction",
                         color="gray", fontsize=10, pad=8)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.info(f"SHAP explanation unavailable: {e}")
    else:
        st.info("SHAP explanations will appear once the model has been trained.")

    # Cultural notes
    st.markdown("#### Cultural notes")
    st.caption(
        "The following items involve speech or language behaviours. "
        "Responses may be influenced by linguistic and cultural differences "
        "in Sesotho-speaking contexts."
    )
    for item_id, info in result["cultural_notes"].items():
        with st.expander(f"{item_id} — Response: {info['response']}"):
            st.write(info["note"])

    st.divider()
    st.caption(
        "Research prototype only. This tool does not constitute a clinical diagnosis. "
        "Results should always be interpreted alongside professional assessment."
    )


#  About 
def render_about():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">Autism Risk Screening</div>
        <p class="hero-sub">
            A machine learning screening tool for early autism risk identification
            in young children, designed with the Southern African context in mind.
            Trained on Q-CHAT-10 data from three countries and calibrated using
            the Lesotho Demographic and Health Survey 2023–24.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("1,601", "Training records"),
        ("10",    "Screening items"),
        ("18–36", "Age range (months)"),
        ("0.710", "AUROC on test set"),
    ]
    for col, (num, label) in zip([c1, c2, c3, c4], stats):
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{num}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown("#### How it works")
        steps = [
            ("Step 1", "Caregiver fills in the Q-CHAT-10 questionnaire"),
            ("Step 2", "Child age, sex, and health indicators are recorded"),
            ("Step 3", "Two XGBoost models process behavioural and demographic inputs"),
            ("Step 4", "Outputs are combined using late fusion averaging"),
            ("Step 5", "Threshold is adjusted using Lesotho DHS health indicators"),
            ("Step 6", "A risk score and screening recommendation are returned"),
        ]
        for num, text in steps:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-num">{num}</div>
                <div class="step-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("#### Data sources")

        sources = [
            ("Q-CHAT-10 training data",
             "Unified toddler screening dataset (Abbadi & Thabtah, 2025). "
             "1,601 records filtered to ages 18–36 months from New Zealand, "
             "Saudi Arabia, and Poland."),
            ("Test set",
             "Polish clinical dataset (Niedźwiecka et al., 2020). "
             "252 records with confirmed ASD and typically developing cases."),
            ("Threshold calibration",
             "Lesotho Demographic and Health Survey 2023–24 (LSKR81DT). "
             "Stunting, anaemia, caregiver presence, and rural residence indicators."),
            ("Cultural alignment",
             "SADiLaR Sesotho sa Leboa child speech corpus. "
             "Naturalistic therapist-child interaction recordings used for "
             "linguistic analysis of speech-related Q-CHAT items."),
        ]
        for title, body in sources:
            st.markdown(f"""
            <div class="source-block">
                <div class="source-title">{title}</div>
                <div class="source-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Limitations")
        st.markdown("""
        <div class="limit-box">
            This is a screening tool and does not constitute a clinical diagnosis.
            The system has not been validated with children or caregivers in Lesotho.
            Results must be interpreted alongside professional clinical assessment.
            The SADiLaR corpus represents Sesotho sa Leboa, which is closely related
            to but not identical to Sesotho spoken in Lesotho.
        </div>
        """, unsafe_allow_html=True)


# Fairness tab 
def render_fairness():
    st.markdown("### Fairness evaluation")
    st.markdown(
        "Subgroup performance analysis across age and sex. "
        "Overall F1 = 0.708. A disparity is flagged where subgroup F1 "
        "falls more than 0.05 below the overall."
    )

    fairness_path = "outputs/fairness/subgroup_results.csv"
    if os.path.exists(fairness_path):
        df = pd.read_csv(fairness_path)
        st.dataframe(df, use_container_width=True)

        # Simple bar chart using matplotlib — transparent background for dark mode
        fig, ax = plt.subplots(figsize=(7, 2.5))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        colours = ["#e74c3c" if f < 0.658 else "#4f6ef7"
                   for f in df["f1"]]
        ax.barh(df["subgroup"], df["f1"], color=colours, height=0.5)
        ax.axvline(0.708, color="gray", linewidth=1, linestyle="--",
                   label="Overall F1 = 0.708", alpha=0.7)
        ax.set_xlabel("F1 score", color="gray", fontsize=9)
        ax.tick_params(colors="gray", labelsize=9)
        ax.legend(fontsize=8, labelcolor="gray",
                  framealpha=0, loc="lower right")
        for spine in ax.spines.values():
            spine.set_visible(False)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info(
            "Fairness evaluation results will appear here after "
            "model evaluation has been completed."
        )


# Main 
def main():
    st.title("Autism Risk Screening")
    st.markdown(
        "Early developmental risk assessment for children aged 18–36 months. "
        "Designed for use in Southern African low-resource contexts."
    )

    tab_screen, tab_about, tab_fairness = st.tabs(["Screening", "About", "Fairness"])

    with tab_screen:
        age_months, sex, stunted, anaemic, no_caregiver, rural = render_sidebar()
        responses = render_qchat_form()

        if st.button("Generate Assessment", type="primary", use_container_width=True):
            predictor = get_predictor()
            result = predictor.predict(
                responses    = responses,
                age_months   = age_months,
                sex          = sex,
                stunted      = stunted,
                anaemic      = anaemic,
                no_caregiver = no_caregiver,
                rural        = rural,
            )
            render_results(result, responses)

    with tab_about:
        render_about()

    with tab_fairness:
        render_fairness()


if __name__ == "__main__":
    main()