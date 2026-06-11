# Autism Risk Screening Application

import os
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from predictor import get_predictor, QCHAT_ITEMS, RESPONSE_OPTIONS

# Configure Streamlit page
st.set_page_config(
    page_title="Autism Risk Screening",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar inputs
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

# Q-CHAT-10 questionnaire form
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

# Results panel
def render_results(result: dict, responses: dict):
    prob    = result["prob_calibrated"]
    at_risk = result["at_risk"]

    st.divider()
    st.subheader("Screening Results")

    if result["demo_mode"]:
        st.warning("Models not loaded. Showing illustrative results only.")

    if at_risk:
        st.error("Screening Result: At Risk")
    else:
        st.success("Screening Result: Not At Risk")

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Probability",   f"{prob:.1%}")
    col2.metric("Decision Threshold", f"{result['threshold']:.2f}")
    col3.metric("Classification",     "At Risk" if at_risk else "Not At Risk")

    st.info(result.get("validation_note", "Model validation details are unavailable."))

    st.markdown("#### Risk Probability")
    st.progress(prob, text=f"{prob:.1%}")

    # SHAP feature contributions
    st.markdown("#### Feature Contributions")
    predictor = get_predictor()
    if SHAP_AVAILABLE and predictor.models_loaded:
        try:
            X_beh      = predictor.encode_responses(responses)
            explainer  = shap.TreeExplainer(predictor.model_beh)
            shap_vals  = explainer.shap_values(X_beh)
            vals       = shap_vals[0] if isinstance(shap_vals, list) else shap_vals[0]
            feat_names = [f"Q{i}" for i in range(1, 11)]

            fig, ax = plt.subplots(figsize=(8, 3))
            colours = ["#e74c3c" if v > 0 else "#2ecc71" for v in vals]
            ax.barh(feat_names, vals, color=colours)
            ax.axvline(0, color="black", linewidth=0.8)
            ax.set_xlabel("SHAP Value (positive = towards At Risk)")
            ax.set_title("Feature contribution to prediction")
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.info(f"SHAP explanation unavailable: {e}")
    else:
        st.info("SHAP explanations will appear once the model has been trained.")

    # Cultural notes
    st.markdown("#### Cultural Notes")
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
        "Research prototype. This tool provides screening results only "
        "and should not be used as a medical diagnosis."
    )

# About page
def render_about():
    st.markdown("""
        <style>
        .about-hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2rem;
        }
        .about-hero h2 { color: white; margin: 0 0 0.5rem 0; font-size: 1.8rem; }
        .about-hero p  { color: rgba(255,255,255,0.88); margin: 0; font-size: 1.05rem; }
        .stat-card {
            background: #f8f9ff;
            border: 1px solid #e0e4ff;
            border-radius: 12px;
            padding: 1.2rem 1rem;
            text-align: center;
        }
        .stat-number { font-size: 2rem; font-weight: 700; color: #667eea; }
        .stat-label  { font-size: 0.85rem; color: #666; margin-top: 0.2rem; }
        .step-card {
            background: #ffffff;
            border-left: 4px solid #667eea;
            padding: 0.9rem 1.2rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 0.8rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        .step-num  { font-weight: 700; color: #667eea; font-size: 0.8rem; letter-spacing: 1px; }
        .step-text { color: #333; margin-top: 0.2rem; font-size: 0.95rem; }
        .limit-box {
            background: #fff8f0;
            border: 1px solid #ffd0a0;
            border-radius: 10px;
            padding: 1rem 1.2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="about-hero">
            <h2>Autism Risk Screening</h2>
            <p>A machine learning tool for early autism risk identification in young children,
            designed with the Southern African context in mind.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("1,601", "Training records"),
        ("10",    "Screening items"),
        ("18–36", "Age range (months)"),
        ("2",     "Model inputs"),
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
        st.markdown("#### How It Works")
        steps = [
            ("STEP 1", "Caregiver fills in the Q-CHAT-10 questionnaire"),
            ("STEP 2", "Child age, sex, and health indicators are recorded"),
            ("STEP 3", "Two XGBoost models process behavioural and demographic inputs separately"),
            ("STEP 4", "Outputs are combined using late fusion"),
            ("STEP 5", "Threshold is adjusted using Lesotho DHS health indicators"),
            ("STEP 6", "A risk score and screening recommendation are returned"),
        ]
        for num, text in steps:
            st.markdown(f"""
                <div class="step-card">
                    <div class="step-num">{num}</div>
                    <div class="step-text">{text}</div>
                </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("#### Data Sources")
        st.markdown("""
**Q-CHAT-10 Training Data**
- Unified toddler screening dataset (Abbadi & Thabtah, 2025)
- 1,601 records filtered to ages 18–36 months

**Test Set**
- Polish clinical dataset (Niedźwiecka et al., 2020)
- Q-CHAT-25, items 1–10 used
    - Used as the test set for text-based result summaries

**Calibration**
- Lesotho Demographic and Health Survey 2023–24
- South African Road to Health developmental milestones

**Cultural Alignment**
- SADiLaR Sesotho sa Leboa child speech corpus
        """)

        st.markdown("#### Limitations")
        st.markdown("""
            <div class="limit-box">
            This is a screening tool — not a clinical diagnosis.<br><br>
            The system has not yet been validated with children or caregivers in Lesotho.
            Results should always be interpreted alongside professional clinical assessment.
            </div>
        """, unsafe_allow_html=True)

# Main
def main():
    st.title("Autism Risk Screening")
    st.markdown("Screening tool for developmental risk assessment in young children.")

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
        st.markdown("### Fairness Evaluation")
        st.markdown(
            "Subgroup performance analysis across age and sex."
        )
        fairness_path = "outputs/fairness/subgroup_results.csv"
        if os.path.exists(fairness_path):
            df = pd.read_csv(fairness_path)
            st.dataframe(df, use_container_width=True)
        else:
            st.info(
                "Fairness evaluation results will be displayed "
                "after model evaluation has been completed."
            )

if __name__ == "__main__":
    main()