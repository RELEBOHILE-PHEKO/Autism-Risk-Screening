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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── tokens (Lesotho screening identity: deep navy + savanna gold) ── */
:root {
    --brand:        #1A4E6B;
    --brand-light:  #2A6E93;
    --brand-muted:  rgba(26, 78, 107, 0.10);
    --accent:       #C9943A;
    --accent-light: #F0C060;
    --risk-low:     #1A7A4A;
    --risk-mid:     #D4760A;
    --risk-high:    #B03030;
    --ink:          #1C2B3A;
    --muted-ink:    #5A6E7F;
    --border:       #D8E2EA;
    --radius:       14px;
    --radius-sm:    9px;
    --display-font: 'Fraunces', Georgia, serif;
    --body-font:    'Inter', -apple-system, sans-serif;
}

h1, h2, h3, .hero-title, .gauge-tier-label {
    font-family: var(--display-font) !important;
    letter-spacing: -0.01em;
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
    position: relative;
    overflow: hidden;
    padding: 1.8rem 1.8rem 1.6rem;
    border-radius: var(--radius);
    background: linear-gradient(160deg, var(--brand) 0%, #0F3349 100%);
    margin-bottom: 1.8rem;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(201,148,58,.16);
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(201,148,58,.18);
    border: 1px solid rgba(201,148,58,.4);
    border-radius: 20px;
    padding: 3px 12px;
    margin-bottom: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent-light);
    position: relative;
    z-index: 1;
}
.hero-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.4rem 0;
    position: relative;
    z-index: 1;
}
.hero-title em {
    font-style: normal;
    color: var(--accent-light);
}
.hero-sub {
    font-family: var(--body-font);
    font-size: 0.95rem;
    color: rgba(255,255,255,.7);
    margin: 0;
    line-height: 1.55;
    position: relative;
    z-index: 1;
    max-width: 640px;
}

/* ── risk gauge (signature element) ── */
.gauge-card {
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
    background: linear-gradient(160deg, var(--brand) 0%, #0F3349 100%);
    border-radius: var(--radius);
    padding: 1.6rem 1.8rem;
    margin: 1rem 0 1.4rem;
}
.gauge-svg-wrap { flex-shrink: 0; }
.gauge-readout { flex: 1; min-width: 180px; }
.gauge-score {
    font-family: var(--display-font);
    font-size: 2.6rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.gauge-tier-label {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
}
.gauge-tier-label.low    { background: rgba(26,122,74,.25);  color: #7BE0A8; }
.gauge-tier-label.mid    { background: rgba(212,118,10,.25); color: var(--accent-light); }
.gauge-tier-label.high   { background: rgba(176,48,48,.28);  color: #F5A3A3; }

/* ── risk banner (replaces default st.error/success for tier control) ── */
.risk-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.9rem 1.1rem;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
}
.risk-banner.low  { background: rgba(26,122,74,.10);  color: var(--risk-low);  border: 1px solid rgba(26,122,74,.3); }
.risk-banner.mid  { background: rgba(212,118,10,.10); color: var(--risk-mid);  border: 1px solid rgba(212,118,10,.3); }
.risk-banner.high { background: rgba(176,48,48,.10);  color: var(--risk-high); border: 1px solid rgba(176,48,48,.3); }

/* ── cultural flag cards ── */
.flag-card {
    background: transparent;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
}
.flag-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.flag-card-name { font-size: 0.88rem; font-weight: 700; }
.flag-pill {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    background: rgba(212,118,10,.14);
    color: var(--risk-mid);
}
.flag-card-desc { font-size: 0.85rem; opacity: 0.75; line-height: 1.5; }

/* ── risk meter (legacy, kept for compatibility) ── */
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
    jaundice    = st.sidebar.checkbox("History of jaundice at birth")
    family_asd  = st.sidebar.checkbox("Immediate family member with ASD")

    st.sidebar.divider()
    st.sidebar.header("Contextual Indicators")
    st.sidebar.caption("From the Lesotho DHS 2023–24. Leave unchecked if unknown.")

    stunted      = st.sidebar.checkbox("Child is stunted")
    anaemic      = st.sidebar.checkbox("Child is anaemic")
    no_caregiver = st.sidebar.checkbox("Neither biological parent present in household")
    rural        = st.sidebar.checkbox("Rural residence")

    return age_months, sex, jaundice, family_asd, stunted, anaemic, no_caregiver, rural


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


#  Risk gauge (signature element) 
def _risk_tier(prob: float):
    if prob < 0.35:
        return "low", "LOW RISK", "#1A7A4A"
    elif prob < 0.60:
        return "mid", "MODERATE RISK — MONITOR", "#D4760A"
    else:
        return "high", "AT RISK — REFER", "#B03030"


def render_gauge_svg(prob: float) -> str:
    tier, _, _ = _risk_tier(prob)
    # semicircular arc: full arc length ~ 283 (matches r=90 half-circumference)
    arc_len = 283
    offset = arc_len * (1 - prob)
    return f"""
    <svg viewBox="0 0 220 120" width="220" height="120" style="overflow:visible;">
        <path d="M 20 110 A 90 90 0 0 1 200 110"
              fill="none" stroke="rgba(255,255,255,.15)" stroke-width="14" stroke-linecap="round"/>
        <path d="M 20 110 A 90 90 0 0 1 200 110"
              fill="none" stroke="url(#gaugeGrad)" stroke-width="14" stroke-linecap="round"
              stroke-dasharray="{arc_len}" stroke-dashoffset="{offset}"/>
        <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#1A7A4A"/>
                <stop offset="50%" stop-color="#D4760A"/>
                <stop offset="100%" stop-color="#B03030"/>
            </linearGradient>
        </defs>
        <text x="14" y="128" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">Low</text>
        <text x="96" y="108" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">Mid</text>
        <text x="185" y="128" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">High</text>
    </svg>
    """


# Results 
def render_results(result: dict, responses: dict):
    prob    = result["prob_calibrated"]
    at_risk = result["at_risk"]
    tier, tier_label, _ = _risk_tier(prob)

    st.divider()
    st.subheader("Screening Results")

    if result["demo_mode"]:
        st.warning("Models not loaded. Showing illustrative results only.")

    # Signature element: semicircular risk gauge
    st.markdown(f"""
    <div class="gauge-card">
        <div class="gauge-svg-wrap">{render_gauge_svg(prob)}</div>
        <div class="gauge-readout">
            <div class="gauge-score">{prob:.2f}</div>
            <span class="gauge-tier-label {tier}">{tier_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Risk banner (tier-coded, not generic red/green)
    banner_text = {
        "low":  "Screening result: Not at risk",
        "mid":  "Screening result: Moderate risk — recommend monitoring",
        "high": "Screening result: At risk — recommend referral for follow-up",
    }[tier]
    st.markdown(f"""
    <div class="risk-banner {tier}">{banner_text}</div>
    """, unsafe_allow_html=True)

    # Metric row
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Probability",   f"{prob:.1%}")
    col2.metric("Decision Threshold", f"{result['threshold']:.2f}")
    col3.metric("Classification",     "At Risk" if at_risk else "Not At Risk")

    st.info(result.get("validation_note", "Model validation details unavailable."))

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
            colours = ["#B03030" if v > 0 else "#1A4E6B" for v in vals]
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
    st.markdown("#### Cultural alignment — flagged items")
    st.caption(
        "The following items involve speech or language behaviours. "
        "Responses may be influenced by linguistic and cultural differences "
        "in Sesotho-speaking contexts."
    )
    for item_id, info in result["cultural_notes"].items():
        st.markdown(f"""
        <div class="flag-card">
            <div class="flag-card-top">
                <span class="flag-card-name">{item_id} — Response: {info['response']}</span>
                <span class="flag-pill">⚠ Review</span>
            </div>
            <div class="flag-card-desc">{info['note']}</div>
        </div>
        """, unsafe_allow_html=True)

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
        ("0.814", "AUROC on test set"),
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
        "Overall F1 = 0.768. A disparity is flagged where subgroup F1 "
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
        colours = ["#B03030" if f < 0.718 else "#1A4E6B"
                   for f in df["f1"]]
        ax.barh(df["subgroup"], df["f1"], color=colours, height=0.5)
        ax.axvline(0.768, color="gray", linewidth=1, linestyle="--",
                   label="Overall F1 = 0.768", alpha=0.7)
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
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">● Research Prototype</div>
        <div class="hero-title">Early ASD Risk Screening for <em>Southern Africa</em></div>
        <p class="hero-sub">
            A context-adapted screening tool for children aged 18–36 months,
            calibrated using the Lesotho Demographic and Health Survey 2023–24.
            Not a clinical diagnosis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_screen, tab_about, tab_fairness = st.tabs(["Screening", "About", "Fairness"])

    with tab_screen:
        age_months, sex, jaundice, family_asd, stunted, anaemic, no_caregiver, rural = render_sidebar()
        responses = render_qchat_form()

        if st.button("Generate Assessment", type="primary", use_container_width=True):
            predictor = get_predictor()
            result = predictor.predict(
                responses    = responses,
                age_months   = age_months,
                sex          = sex,
                jaundice     = jaundice,
                family_asd   = family_asd,
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