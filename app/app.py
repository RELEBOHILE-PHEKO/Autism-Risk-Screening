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

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
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
h1, h2, h3, .hero-title, .gauge-tier-label { font-family: var(--display-font) !important; letter-spacing: -0.01em; }
.badge-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; position: relative; z-index: 1; }
.badge-chip {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em;
    padding: 5px 12px; border-radius: 20px;
    background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.22);
    color: rgba(255,255,255,.92);
}
.badge-chip.warn { background: rgba(212,118,10,.20); border-color: rgba(240,192,96,.5); color: var(--accent-light); }
.pill-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 1.2rem; position: relative; z-index: 1; }
.pill {
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16);
    border-radius: var(--radius-sm); padding: 0.7rem 1rem; min-width: 118px;
}
.pill-num { font-family: var(--display-font); font-size: 1.35rem; font-weight: 700; color: #fff; line-height: 1.1; }
.pill-label { font-size: 0.7rem; color: rgba(255,255,255,.62); margin-top: 2px; }
.exec-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0.8rem 0 1.4rem; }
.exec-card {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem 1.1rem; background: transparent;
}
.exec-card-title { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--brand); margin-bottom: 4px; }
.exec-card-body { font-size: 0.88rem; opacity: 0.82; line-height: 1.5; }
.unique-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 0.6rem 0 1.6rem; }
.unique-card {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.1rem 1.15rem; background: transparent; position: relative;
}
.unique-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
    background: var(--accent); border-radius: var(--radius) 0 0 var(--radius);
}
.unique-num { font-family: var(--display-font); font-size: 0.85rem; font-weight: 700; color: var(--accent); margin-bottom: 6px; display: block; }
.unique-title { font-size: 0.95rem; font-weight: 700; color: var(--ink); margin-bottom: 4px; }
.unique-body { font-size: 0.84rem; opacity: 0.75; line-height: 1.5; }
.safety-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 0.6rem 0 1.4rem; }
.safety-col { border-radius: var(--radius); padding: 1rem 1.15rem; }
.safety-col.can  { background: rgba(26,122,74,.07);  border: 1px solid rgba(26,122,74,.25); }
.safety-col.cant { background: rgba(176,48,48,.07);  border: 1px solid rgba(176,48,48,.25); }
.safety-head { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 8px; }
.safety-col.can .safety-head  { color: var(--risk-low); }
.safety-col.cant .safety-head { color: var(--risk-high); }
.safety-item { font-size: 0.85rem; opacity: 0.85; line-height: 1.7; }
@media (max-width: 700px) { .safety-grid { grid-template-columns: 1fr; } }
.stat-card { border: 1px solid var(--border); border-radius: var(--radius); padding: 1.1rem 1rem; text-align: center; background: transparent; }
.stat-number { font-size: 1.9rem; font-weight: 700; color: var(--brand); line-height: 1.1; }
.stat-label { font-size: 0.8rem; margin-top: 0.3rem; opacity: 0.65; }
.step-card { border-left: 3px solid var(--brand); padding: 0.75rem 1rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; margin-bottom: 0.6rem; background: var(--brand-muted); }
.step-num { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; color: var(--brand); text-transform: uppercase; }
.step-text { font-size: 0.92rem; margin-top: 0.15rem; }
.source-block { border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.1rem; margin-bottom: 0.8rem; background: transparent; }
.source-title { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--brand); margin-bottom: 0.3rem; }
.source-body { font-size: 0.88rem; opacity: 0.8; line-height: 1.55; }
.limit-box { border: 1px solid rgba(255, 180, 50, 0.4); border-radius: var(--radius); padding: 1rem 1.1rem; background: rgba(255, 180, 50, 0.07); font-size: 0.88rem; line-height: 1.6; }
.hero { position: relative; overflow: hidden; padding: 1.9rem 1.9rem 1.7rem; border-radius: var(--radius); background: linear-gradient(160deg, var(--brand) 0%, #0F3349 100%); margin-bottom: 1.8rem; }
.hero::before { content: ''; position: absolute; top: -50px; right: -50px; width: 160px; height: 160px; border-radius: 50%; background: rgba(201,148,58,.16); }
.hero::after { content: ''; position: absolute; bottom: -70px; left: -40px; width: 200px; height: 200px; border-radius: 50%; background: rgba(42,110,147,.20); }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 6px; background: rgba(201,148,58,.18); border: 1px solid rgba(201,148,58,.4); border-radius: 20px; padding: 3px 12px; margin-bottom: 12px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent-light); position: relative; z-index: 1; }
.hero-title { font-size: 1.9rem; font-weight: 700; color: #fff; margin: 0 0 0.5rem 0; position: relative; z-index: 1; }
.hero-title em { font-style: normal; color: var(--accent-light); }
.hero-sub { font-family: var(--body-font); font-size: 0.98rem; color: rgba(255,255,255,.72); margin: 0; line-height: 1.6; position: relative; z-index: 1; max-width: 680px; }
.gauge-card { display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; background: linear-gradient(160deg, var(--brand) 0%, #0F3349 100%); border-radius: var(--radius); padding: 1.6rem 1.8rem; margin: 1rem 0 1.4rem; }
.gauge-svg-wrap { flex-shrink: 0; }
.gauge-readout { flex: 1; min-width: 180px; }
.gauge-score { font-family: var(--display-font); font-size: 2.6rem; font-weight: 700; color: #fff; line-height: 1; margin-bottom: 0.4rem; }
.gauge-tier-label { display: inline-block; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 5px 14px; border-radius: 20px; }
.gauge-tier-label.low  { background: rgba(26,122,74,.25);  color: #7BE0A8; }
.gauge-tier-label.mid  { background: rgba(212,118,10,.25); color: var(--accent-light); }
.gauge-tier-label.high { background: rgba(176,48,48,.28);  color: #F5A3A3; }
.risk-banner { display: flex; align-items: center; gap: 12px; padding: 0.9rem 1.1rem; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.95rem; margin-bottom: 0.8rem; }
.risk-banner.low  { background: rgba(26,122,74,.10);  color: var(--risk-low);  border: 1px solid rgba(26,122,74,.3); }
.risk-banner.mid  { background: rgba(212,118,10,.10); color: var(--risk-mid);  border: 1px solid rgba(212,118,10,.3); }
.risk-banner.high { background: rgba(176,48,48,.10);  color: var(--risk-high); border: 1px solid rgba(176,48,48,.3); }
.flag-card { background: transparent; border: 1.5px solid var(--border); border-radius: var(--radius-sm); padding: 0.9rem 1rem; margin-bottom: 0.6rem; }
.flag-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.flag-card-name { font-size: 0.88rem; font-weight: 700; }
.flag-pill { font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 20px; background: rgba(212,118,10,.14); color: var(--risk-mid); }
.flag-card-desc { font-size: 0.85rem; opacity: 0.75; line-height: 1.5; }
.cta-banner {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem 1.3rem; margin: 0.4rem 0 1.6rem;
    background: linear-gradient(90deg, var(--brand-muted), transparent);
}
.cta-text { font-size: 0.92rem; font-weight: 600; color: var(--ink); }
.cta-sub { font-size: 0.8rem; opacity: 0.65; margin-top: 2px; }
.stDataFrame { border-radius: var(--radius); overflow: hidden; }
.notice-box { display: flex; align-items: flex-start; gap: 8px; padding: 0.8rem 1rem; border-radius: var(--radius-sm); font-size: 0.88rem; line-height: 1.5; margin-bottom: 0.8rem; }
.notice-box.warn { background: rgba(212,118,10,.08); border: 1px solid rgba(212,118,10,.25); color: var(--muted-ink); }
.notice-box.info { background: var(--brand-muted); border: 1px solid var(--border); color: var(--muted-ink); }
section[data-testid="stSidebar"] .stCaption { opacity: 0.6; }
</style>
""", unsafe_allow_html=True)


def icon(name: str, size: int = 14, color: str = "currentColor") -> str:
    """Small inline monochrome SVG icons (hand-authored, no external assets)."""
    paths = {
        "pin": '<path d="M12 22s7-7.58 7-12A7 7 0 0 0 5 10c0 4.42 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
        "child": '<circle cx="12" cy="7" r="3.2"/><path d="M6 21v-2a6 6 0 0 1 12 0v2"/>',
        "speech": '<path d="M4 4h16v11H8l-4 4V4z"/>',
        "warning": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "check": '<circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-6"/>',
        "cross": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
        "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="11"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    }
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:-2px; display:inline-block; margin-right:4px;">{paths[name]}</svg>')


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

    st.sidebar.caption("Optional — additional maternal & birth indicators")
    low_maternal_edu = st.sidebar.checkbox("Mother has no/primary education only")
    low_wealth        = st.sidebar.checkbox("Household in lowest two wealth quintiles")
    inadequate_anc    = st.sidebar.checkbox("Fewer than 4 antenatal care visits")
    small_birth        = st.sidebar.checkbox("Child was small/very small at birth")
    home_delivery      = st.sidebar.checkbox("Child was born at home")
    short_interval      = st.sidebar.checkbox("Birth interval under 24 months")

    return (age_months, sex, jaundice, family_asd, stunted, anaemic, no_caregiver, rural,
            low_maternal_edu, low_wealth, inadequate_anc, small_birth, home_delivery, short_interval)


def _bordered_container():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def render_qchat_form():
    st.subheader("Q-CHAT-10 Responses")
    st.caption("Select the response that best describes the child's typical behaviour.")

    responses = {}
    cols = st.columns(2)
    for i, (item_id, question) in enumerate(QCHAT_ITEMS):
        with cols[i % 2]:
            with _bordered_container():
                st.markdown(f"**{item_id}.** {question}")
                responses[item_id] = st.selectbox(
                    label=f"Response for {item_id}",
                    options=list(RESPONSE_OPTIONS.keys()),
                    key=f"qchat_{item_id}",
                    label_visibility="collapsed",
                )
    return responses


def _risk_tier(prob: float):
    """
    Tier cutoffs for a PRIOR-CORRECTED probability, where the deployment
    ASD prevalence is calibrated to ~1% (Zeidan et al., 2022), not the
    ~42% training-set prevalence. Raw probabilities cluster near 0 after
    correction, so cutoffs are set relative to the model's own decision
    threshold rather than the old 0.35/0.60 scale, which assumed
    uncorrected probabilities and would show nearly every child as "low
    risk" regardless of actual status.
    """
    predictor = get_predictor()
    thr = getattr(predictor, "threshold", None) or 0.01
    if prob < thr:
        return "low", "LOW RISK", "#1A7A4A"
    elif prob < thr * 3:
        return "mid", "MODERATE RISK — MONITOR", "#D4760A"
    else:
        return "high", "AT RISK — REFER", "#B03030"


def render_gauge_svg(prob: float) -> str:
    tier, _, _ = _risk_tier(prob)
    predictor = get_predictor()
    thr = getattr(predictor, "threshold", None) or 0.01
    # Display scale is relative to ~5x the decision threshold so the arc
    # is visually meaningful even though raw probabilities are tiny after
    # prior correction (deployment prevalence ~1%).
    display_max = max(thr * 5, 0.05)
    frac = min(prob / display_max, 1.0)
    arc_len = 283
    offset = arc_len * (1 - frac)
    return f"""<svg viewBox="0 0 220 120" width="220" height="120" style="overflow:visible;"><path d="M 20 110 A 90 90 0 0 1 200 110" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="14" stroke-linecap="round"/><path d="M 20 110 A 90 90 0 0 1 200 110" fill="none" stroke="url(#gaugeGrad)" stroke-width="14" stroke-linecap="round" stroke-dasharray="{arc_len}" stroke-dashoffset="{offset}"/><defs><linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#1A7A4A"/><stop offset="50%" stop-color="#D4760A"/><stop offset="100%" stop-color="#B03030"/></linearGradient></defs><text x="14" y="128" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">Low</text><text x="96" y="108" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">Mid</text><text x="185" y="128" font-size="10" fill="rgba(255,255,255,.5)" font-family="Inter, sans-serif">High</text></svg>"""


def render_comparison_chart():
    st.markdown("### Capability comparison")

    capability_df = pd.DataFrame(
        {
            "This app": [1, 1, 1, 1, 1],
            "M-CHAT-R/F (generic use)": [0, 0, 0, 0, 1],
            "Q-CHAT-10 form only": [0, 1, 0, 0, 1],
        },
        index=[
            "Local threshold calibration",
            "Behaviour + speech signals",
            "Per-child explainability",
            "Subgroup fairness audit",
            "Free/open access",
        ],
    )

    counts = capability_df.sum(axis=0).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(7, 2.6))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.barh(counts.index, counts.values, color=["#9AA7B2", "#9AA7B2", "#1A4E6B"])
    ax.set_xlim(0, 5)
    ax.set_xlabel("Capabilities present (out of 5)", color="gray", fontsize=9)
    ax.tick_params(colors="gray", labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    st.pyplot(fig)
    plt.close(fig)

    show_df = capability_df.replace({1: "✓", 0: "—"}).T
    st.dataframe(show_df, use_container_width=True)


def render_results(result: dict, responses: dict):
    st.markdown("### Screening result")

    prob = float(result.get("prob_calibrated", result.get("prob_fused", 0.0)))
    tier, tier_label, _ = _risk_tier(prob)
    thr = float(result.get("threshold", 0.5))

    banner_text = (
        "Higher likelihood of autism-related traits. Please refer for formal developmental assessment."
        if result.get("at_risk", False)
        else "No elevated risk flag at the selected threshold. Continue developmental monitoring."
    )
    st.markdown(
        f'<div class="risk-banner {tier}">{icon("info", 15)} {banner_text}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="gauge-card">
        <div class="gauge-svg-wrap">{render_gauge_svg(prob)}</div>
        <div class="gauge-readout">
            <div class="gauge-score">{_fmt_pct(prob)}</div>
            <div class="gauge-tier-label {tier}">{tier_label}</div>
            <div style="margin-top:8px;font-size:.82rem;color:rgba(255,255,255,.78);">
                Decision threshold: {_fmt_pct(thr)}
            </div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Calibrated risk", _fmt_pct(prob))
    c2.metric("Behavioural model", _fmt_pct(result.get("prob_behavioural", 0.0)))
    dem = result.get("prob_demographic", None)
    c3.metric("Demographic model", "N/A" if dem is None else _fmt_pct(dem))

    st.markdown(
        f'<div class="notice-box info">{icon("info", 15)} '
        f'{result.get("validation_note", "Model details unavailable.")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Model mode: {str(result.get('model_mode', 'unknown')).upper()}")

    notes = result.get("cultural_notes", {}) or {}
    if notes:
        st.markdown("#### Cultural interpretation flags (speech-related items)")
        for item_id, payload in notes.items():
            st.markdown(
                f"""<div class="flag-card">
                <div class="flag-card-top">
                    <div class="flag-card-name">{item_id}: response = {payload.get("response","—")}</div>
                    <span class="flag-pill">Context note</span>
                </div>
                <div class="flag-card-desc">{payload.get("note","")}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def _fmt_pct(x: float) -> str:
    return f"{float(x) * 100:.1f}%"


def render_overview():
    pred = get_predictor()
    info = pred.runtime_summary()

    auroc_txt = f"{info['reference_auroc']:.3f}" if info["reference_auroc"] is not None else "n/a"
    thr_txt = f"{info['threshold']:.3f}" if info["threshold"] is not None else "n/a"
    mode_txt = info["mode"].upper()

    st.markdown(
        f"""<div class="hero"><div class="hero-eyebrow">● Research Prototype — Not a Clinical Diagnosis</div>
        <div class="badge-row"><span class="badge-chip">{icon("pin", 12)} Lesotho-calibrated</span>
        <span class="badge-chip">{icon("child", 12)} Ages 18–36 months</span>
        <span class="badge-chip">{icon("speech", 12)} Behaviour + speech signals</span>
        <span class="badge-chip warn">{icon("warning", 12)} Screening only — not diagnostic</span></div>
        <div class="hero-title">Autism Risk Screening for <em>Southern Africa</em></div>
        <p class="hero-sub">A caregiver-facing screener using saved, validated model artifacts from this project to estimate referral priority.</p>
        <div class="pill-row"><div class="pill"><div class="pill-num">1,601</div><div class="pill-label">Training records</div></div>
        <div class="pill"><div class="pill-num">{auroc_txt}</div><div class="pill-label">AUROC (from outputs)</div></div>
        <div class="pill"><div class="pill-num">{thr_txt}</div><div class="pill-label">Active threshold</div></div>
        <div class="pill"><div class="pill-num">{mode_txt}</div><div class="pill-label">Loaded artifacts</div></div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Project overview")
    st.markdown(
        """
This application estimates autism risk using the same trained models produced by the notebook pipeline in this project. It is designed as a research prototype to support early autism screening among young children, particularly in low-resource settings.

The system uses responses from the Q-CHAT-10 questionnaire together with demographic information to generate an autism risk estimate. Predictions are produced using the saved model artifacts created during training and evaluation, ensuring consistency between the notebook experiments and the deployed application.

The underlying pipeline combines machine learning models trained on behavioural screening data from multiple international datasets and incorporates contextual insights from Southern Africa. The project also evaluates model fairness across demographic groups to improve reliability and reduce potential bias.

**Important:** This tool is intended for research and educational purposes only. It does not provide a medical diagnosis and should not replace professional clinical assessment. If you have concerns about a child's development, please consult a qualified healthcare professional.
        """
    )

    st.markdown("### Executive summary")
    st.markdown(
        """<div class="exec-grid"><div class="exec-card"><div class="exec-card-title">What this does</div>
        <div class="exec-card-body">Scores Q-CHAT-10 behavioural responses using an ensemble model, calibrates risk to target population prevalence, adjusts for local health comorbidities, and returns a practical referral recommendation.</div></div>
        <div class="exec-card"><div class="exec-card-title">Geography &amp; data</div>
        <div class="exec-card-body">Model development used multinational toddler screening datasets, with calibration decisions informed by Lesotho DHS indicators (stunting, anaemia) and local language-context review.</div></div>
        <div class="exec-card"><div class="exec-card-title">Who it's for</div>
        <div class="exec-card-body">Caregivers and front-line health workers who need a first-pass risk flag before specialist assessment.</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### What makes this different")
    st.markdown(
        """<div class="unique-grid"><div class="unique-card"><span class="unique-num">01</span><div class="unique-title">Population-aware calibration</div><div class="unique-body">Thresholding is adjusted for local population context (Zeidan et al., 2022 prevalence) rather than copied from a single external cohort.</div></div>
        <div class="unique-card"><span class="unique-num">02</span><div class="unique-title">DHS comorbidity adjustment</div><div class="unique-body">Item responses are reweighted using Lesotho DHS 2023–24 stunting and anaemia prevalence, since these conditions can mimic autism-related behaviours on screening items.</div></div>
        <div class="unique-card"><span class="unique-num">03</span><div class="unique-title">Fairness reporting</div><div class="unique-body">Performance is checked across key subgroups, with gaps reported explicitly.</div></div>
        <div class="unique-card"><span class="unique-num">04</span><div class="unique-title">Culture-aware wording flags</div><div class="unique-body">Speech-related items include context notes where language/culture may affect responses.</div></div></div>""",
        unsafe_allow_html=True,
    )

    render_comparison_chart()

    st.markdown("### What this tool can — and cannot — do")
    st.markdown(
        f"""<div class="safety-grid"><div class="safety-col can"><div class="safety-head">{icon("check", 14)} Can</div>
        <div class="safety-item">• Flag elevated ASD risk for follow-up</div>
        <div class="safety-item">• Support referral prioritization</div>
        <div class="safety-item">• Provide context notes for sensitive items</div></div>
        <div class="safety-col cant"><div class="safety-head">{icon("cross", 14)} Cannot</div>
        <div class="safety-item">• Diagnose autism</div>
        <div class="safety-item">• Replace specialist evaluation</div>
        <div class="safety-item">• Guarantee outcome for an individual child</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="cta-banner">
        <div>
            <div class="cta-text">Ready to try a screening?</div>
            <div class="cta-sub">Open the Screening tab above — it takes about two minutes.</div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_about():
    st.markdown("#### How it works")
    left, right = st.columns(2)

    with left:
        steps = [
            ("Step 1", "Caregiver fills in the Q-CHAT-10 questionnaire"),
            ("Step 2", "Child age, sex, jaundice, and family ASD history are recorded"),
            ("Step 3", "Q-CHAT-10 item responses are reweighted using Lesotho DHS stunting/anaemia prevalence"),
            ("Step 4", "An XGBoost + Logistic Regression behavioural ensemble scores the DHS-adjusted responses"),
            ("Step 5", "The blended probability is rescaled to the target population's ASD prevalence (Zeidan et al., 2022)"),
            ("Step 6", "A risk score, referral category, and per-item explanation are returned"),
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
             "Unified toddler screening dataset. 1,601 records filtered to ages 18–36 months "
             "from New Zealand, Saudi Arabia, and Poland."),
            ("Test set",
             "Polish clinical dataset (Niedźwiecka et al., 2020). "
             "252 records with confirmed ASD and typically developing cases."),
            ("Comorbidity adjustment & threshold calibration",
             "Lesotho Demographic and Health Survey 2023–24 (LSKR81DT). "
             "Stunting, anaemia, caregiver presence, and rural residence indicators."),
            ("Population prevalence prior correction",
             "Global pooled ASD prevalence estimate (Zeidan et al., 2022), used since the "
             "Lesotho DHS does not measure ASD prevalence directly."),
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
        to but not identical to Sesotho spoken in Lesotho. The DHS comorbidity
        adjustment applies a population-level correction; an individual-level
        version was tested but requires primary data linking Q-CHAT-10 responses
        to individual health records, which does not yet exist for Lesotho.
    </div>
    """, unsafe_allow_html=True)


def render_fairness():
    st.markdown("### Fairness evaluation")
    st.markdown(
        "Subgroup performance analysis across age and sex. "
        "A disparity is flagged where subgroup F1 falls more than 0.05 below the overall."
    )

    fairness_path = "outputs/fairness/subgroup_results.csv"
    if os.path.exists(fairness_path):
        df = pd.read_csv(fairness_path)
        st.dataframe(df, use_container_width=True)

        overall_f1 = df["f1"].mean()
        fig, ax = plt.subplots(figsize=(7, 2.5))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        colours = ["#B03030" if f < overall_f1 - 0.05 else "#1A4E6B" for f in df["f1"]]
        ax.barh(df["subgroup"], df["f1"], color=colours, height=0.5)
        ax.axvline(overall_f1, color="gray", linewidth=1, linestyle="--",
                   label=f"Overall F1 = {overall_f1:.3f}", alpha=0.7)
        ax.set_xlabel("F1 score", color="gray", fontsize=9)
        ax.tick_params(colors="gray", labelsize=9)
        ax.legend(fontsize=8, labelcolor="gray", framealpha=0, loc="lower right")
        for spine in ax.spines.values():
            spine.set_visible(False)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info(
            "Fairness evaluation results will appear here after "
            "model evaluation has been completed."
        )


def main():
    tab_overview, tab_screen, tab_about, tab_fairness = st.tabs(
        ["Overview", "Screening", "About", "Fairness"]
    )

    with tab_overview:
        render_overview()

    with tab_screen:
        (age_months, sex, jaundice, family_asd, stunted, anaemic, no_caregiver, rural,
         low_maternal_edu, low_wealth, inadequate_anc, small_birth,
         home_delivery, short_interval) = render_sidebar()
        responses = render_qchat_form()

        if st.button("Generate Assessment", type="primary", use_container_width=True):
            predictor = get_predictor()
            result = predictor.predict(
                responses         = responses,
                age_months        = age_months,
                sex               = sex,
                jaundice          = jaundice,
                family_asd        = family_asd,
                stunted           = stunted,
                anaemic           = anaemic,
                no_caregiver      = no_caregiver,
                rural             = rural,
                low_maternal_edu  = low_maternal_edu,
                low_wealth        = low_wealth,
                inadequate_anc    = inadequate_anc,
                small_birth       = small_birth,
                home_delivery     = home_delivery,
                short_interval    = short_interval,
            )
            render_results(result, responses)

    with tab_about:
        render_about()

    with tab_fairness:
        render_fairness()


if __name__ == "__main__":
    main()