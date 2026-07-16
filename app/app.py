# Autism Risk Screening Application

import os
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from predictor import get_predictor, QCHAT_ITEMS, RESPONSE_OPTIONS

st.set_page_config(
    page_title="Autism Risk Screening",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# DESIGN SYSTEM

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700;9..144,800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
    --brand:        #123C50;
    --brand-2:      #1D7A8C;
    --brand-muted:  rgba(18, 60, 80, 0.08);
    --gold:         #E2A33B;
    --gold-light:   #F2C878;
    --clay:         #C1573D;
    --risk-low:     #2E8B57;
    --risk-mid:     #E2A33B;
    --risk-high:    #C1443A;
    --cream:        #FBF6EC;
    --ink:          #1B2B36;
    --muted-ink:    #5B6B76;
    --border:       #E4DCC9;
    --radius:       18px;
    --radius-sm:    12px;
    --shadow-sm:    0 1px 2px rgba(18,60,80,.06), 0 1px 1px rgba(18,60,80,.04);
    --shadow-md:    0 8px 20px rgba(18,60,80,.10), 0 2px 6px rgba(18,60,80,.06);
    --shadow-lg:    0 18px 40px rgba(18,60,80,.16), 0 6px 14px rgba(18,60,80,.08);
    --display-font: 'Fraunces', Georgia, serif;
    --body-font:    'Manrope', -apple-system, sans-serif;
}
/* FIX: force readable ink-colour text inside all light (#fff / cream) cards,
   regardless of Streamlit's light/dark theme. Without this, body text in
   these cards inherits the theme's near-white default in dark mode and
   becomes invisible against the cards' hardcoded white backgrounds. */
.exec-card, .unique-card, .source-block, .flag-card,
.limit-box, .context-box, .step-card, .cta-banner, .stat-card {
    color: var(--ink);
}
html, body, [class*="css"] { font-family: var(--body-font); }
h1, h2, h3, .hero-title, .gauge-tier-label { font-family: var(--display-font) !important; letter-spacing: -0.01em; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes shimmer { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes sheenSweep { 0% { transform: translateX(-120%) rotate(8deg); } 100% { transform: translateX(220%) rotate(8deg); } }
.fade-in { animation: fadeUp .5s ease both; }
/* ---- signature stripe: a thin Basotho-blanket accent bar ---- */
.stripe-bar {
    height: 6px; width: 100%; border-radius: 6px; margin-bottom: 1.1rem;
    background: repeating-linear-gradient(
        100deg,
        var(--gold) 0 26px,
        var(--clay) 26px 40px,
        var(--brand-2) 40px 66px,
        var(--cream) 66px 74px
    );
    background-size: 300% 100%;
    box-shadow: var(--shadow-sm);
}
/* ---- badges / pills ---- */
.badge-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; position: relative; z-index: 1; }
.badge-chip {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em;
    padding: 6px 13px; border-radius: 20px;
    background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.24);
    color: rgba(255,255,255,.95);
}
.badge-chip.warn { background: rgba(226,163,59,.22); border-color: rgba(242,200,120,.55); color: var(--gold-light); }
.pill-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 1.3rem; position: relative; z-index: 1; }
.pill {
    background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.18);
    border-radius: var(--radius-sm); padding: 0.75rem 1.05rem; min-width: 128px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.12);
    transition: transform .18s ease, background .18s ease;
}
.pill:hover { transform: translateY(-2px); background: rgba(255,255,255,.13); }
.pill-num { font-family: var(--display-font); font-size: 1.4rem; font-weight: 700; color: #fff; line-height: 1.1; }
.pill-label { font-size: 0.7rem; color: rgba(255,255,255,.68); margin-top: 3px; }
/* ---- generic elevated card, used throughout ---- */
.app-card {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.15rem 1.25rem; background: #fff;
    box-shadow: var(--shadow-sm);
    transition: transform .18s ease, box-shadow .18s ease;
}
.app-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.exec-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 0.8rem 0 1.5rem; }
.exec-card { border: 1px solid var(--border); border-radius: var(--radius); padding: 1.1rem 1.2rem; background: #fff; box-shadow: var(--shadow-sm); transition: transform .18s ease, box-shadow .18s ease; }
.exec-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.exec-card-title { font-size: 0.78rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; color: var(--brand-2); margin-bottom: 5px; }
.exec-card-body { font-size: 0.9rem; opacity: 0.85; line-height: 1.55; }
.unique-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 0.7rem 0 1.7rem; }
.unique-card {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.2rem 1.25rem; background: #fff; position: relative; overflow: hidden;
    box-shadow: var(--shadow-sm); transition: transform .18s ease, box-shadow .18s ease;
}
.unique-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.unique-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 5px; height: 100%;
    background: linear-gradient(180deg, var(--gold), var(--clay));
}
.unique-num { font-family: var(--display-font); font-size: 0.82rem; font-weight: 700; color: var(--clay); margin-bottom: 7px; display: block; }
.unique-title { font-size: 0.98rem; font-weight: 800; color: var(--ink); margin-bottom: 5px; }
.unique-body { font-size: 0.86rem; opacity: 0.78; line-height: 1.55; }
.safety-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 0.7rem 0 1.5rem; }
.safety-col { border-radius: var(--radius); padding: 1.1rem 1.25rem; box-shadow: var(--shadow-sm); }
.safety-col.can  { background: rgba(46,139,87,.06);  border: 1px solid rgba(46,139,87,.28); }
.safety-col.cant { background: rgba(193,68,58,.06);  border: 1px solid rgba(193,68,58,.28); }
.safety-head { font-size: 0.78rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 9px; }
.safety-col.can .safety-head  { color: var(--risk-low); }
.safety-col.cant .safety-head { color: var(--risk-high); }
.safety-item { font-size: 0.87rem; opacity: 0.88; line-height: 1.75; }
@media (max-width: 700px) { .safety-grid { grid-template-columns: 1fr; } }
.stat-card { border: 1px solid var(--border); border-radius: var(--radius); padding: 1.15rem 1rem; text-align: center; background: #fff; box-shadow: var(--shadow-sm); }
.stat-number { font-size: 1.95rem; font-weight: 800; color: var(--brand); line-height: 1.1; font-family: var(--display-font); }
.stat-label { font-size: 0.8rem; margin-top: 0.35rem; opacity: 0.65; }
.step-card {
    border-left: 4px solid var(--brand-2); padding: 0.85rem 1.1rem;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0; margin-bottom: 0.65rem;
    background: var(--brand-muted); transition: transform .15s ease;
}
.step-card:hover { transform: translateX(3px); }
.step-num { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; color: var(--brand-2); text-transform: uppercase; }
.step-text { font-size: 0.93rem; margin-top: 0.2rem; }
.source-block { border: 1px solid var(--border); border-radius: var(--radius); padding: 1.05rem 1.15rem; margin-bottom: 0.85rem; background: #fff; box-shadow: var(--shadow-sm); }
.source-title { font-size: 0.78rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; color: var(--brand-2); margin-bottom: 0.35rem; }
.source-body { font-size: 0.89rem; opacity: 0.82; line-height: 1.55; }
.limit-box { border: 1px solid rgba(226,163,59,.45); border-radius: var(--radius); padding: 1.05rem 1.15rem; background: rgba(226,163,59,.08); font-size: 0.89rem; line-height: 1.65; }
.context-box { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.9rem 1.05rem; background: var(--brand-muted); font-size: 0.86rem; line-height: 1.6; }
/* ---- hero ---- */
.hero {
    position: relative; overflow: hidden; padding: 2.1rem 2rem 1.9rem; border-radius: 22px;
    background: linear-gradient(135deg, #0F3145 0%, var(--brand) 45%, #0C4557 100%);
    background-size: 200% 200%;
    animation: shimmer 14s ease-in-out infinite alternate;
    margin-bottom: 1.9rem;
    box-shadow: var(--shadow-lg);
}
.hero::before { content: ''; position: absolute; top: -60px; right: -60px; width: 200px; height: 200px; border-radius: 50%; background: radial-gradient(circle, rgba(226,163,59,.22), transparent 70%); }
.hero::after { content: ''; position: absolute; bottom: -90px; left: -50px; width: 240px; height: 240px; border-radius: 50%; background: radial-gradient(circle, rgba(29,122,140,.28), transparent 70%); }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 6px; background: rgba(226,163,59,.2); border: 1px solid rgba(226,163,59,.42); border-radius: 20px; padding: 4px 13px; margin-bottom: 14px; font-size: 0.71rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--gold-light); position: relative; z-index: 1; }
.hero-title { font-size: 2.05rem; font-weight: 700; color: #fff; margin: 0 0 0.55rem 0; position: relative; z-index: 1; max-width: 640px; line-height: 1.15; }
.hero-title em { font-style: normal; color: var(--gold-light); }
.hero-sub { font-family: var(--body-font); font-size: 1rem; color: rgba(255,255,255,.78); margin: 0; line-height: 1.6; position: relative; z-index: 1; max-width: 640px; }
/* ---- gauge: layered shadow + inner highlight = tactile "3D" dial ---- */
.gauge-card {
    display: flex; align-items: center; gap: 2rem; flex-wrap: wrap;
    background: linear-gradient(160deg, var(--brand) 0%, #0B3244 100%);
    border-radius: var(--radius); padding: 1.7rem 1.9rem; margin: 1rem 0 1.5rem;
    box-shadow: var(--shadow-lg);
    position: relative; overflow: hidden;
}
.gauge-card::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(circle at 20% 15%, rgba(255,255,255,.10), transparent 45%);
}
.gauge-svg-wrap { flex-shrink: 0; filter: drop-shadow(0 6px 14px rgba(0,0,0,.35)); position: relative; z-index: 1; }
.gauge-readout { flex: 1; min-width: 180px; position: relative; z-index: 1; }
.gauge-score { font-family: var(--display-font); font-size: 2.7rem; font-weight: 800; color: #fff; line-height: 1; margin-bottom: 0.45rem; }
.gauge-tier-label { display: inline-block; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; padding: 6px 15px; border-radius: 20px; }
.gauge-tier-label.low  { background: rgba(46,139,87,.28);  color: #8CEBB2; }
.gauge-tier-label.mid  { background: rgba(226,163,59,.28); color: var(--gold-light); }
.gauge-tier-label.high { background: rgba(193,68,58,.30);  color: #F5A8A0; }
.risk-banner { display: flex; align-items: center; gap: 12px; padding: 1rem 1.15rem; border-radius: var(--radius-sm); font-weight: 700; font-size: 0.97rem; margin-bottom: 0.9rem; box-shadow: var(--shadow-sm); }
.risk-banner.low  { background: rgba(46,139,87,.09);  color: var(--risk-low);  border: 1px solid rgba(46,139,87,.3); }
.risk-banner.mid  { background: rgba(226,163,59,.10); color: #A5710B;  border: 1px solid rgba(226,163,59,.35); }
.risk-banner.high { background: rgba(193,68,58,.09);  color: var(--risk-high); border: 1px solid rgba(193,68,58,.3); }
.flag-card { background: #fff; border: 1.5px solid var(--border); border-radius: var(--radius-sm); padding: 0.95rem 1.05rem; margin-bottom: 0.65rem; box-shadow: var(--shadow-sm); }
.flag-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.flag-card-name { font-size: 0.89rem; font-weight: 800; }
.flag-pill { font-size: 0.7rem; font-weight: 800; padding: 3px 11px; border-radius: 20px; background: rgba(226,163,59,.16); color: #A5710B; }
.flag-card-desc { font-size: 0.86rem; opacity: 0.78; line-height: 1.55; }
.cta-banner {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.15rem 1.4rem; margin: 0.5rem 0 1.7rem;
    background: linear-gradient(90deg, rgba(18,60,80,.07), transparent);
    box-shadow: var(--shadow-sm);
}
.cta-text { font-size: 0.96rem; font-weight: 800; color: var(--ink); }
.cta-sub { font-size: 0.82rem; opacity: 0.65; margin-top: 3px; }
.stDataFrame { border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-sm); }
.notice-box { display: flex; align-items: flex-start; gap: 9px; padding: 0.85rem 1.05rem; border-radius: var(--radius-sm); font-size: 0.89rem; line-height: 1.55; margin-bottom: 0.85rem; }
.notice-box.warn { background: rgba(226,163,59,.08); border: 1px solid rgba(226,163,59,.28); color: var(--muted-ink); }
.notice-box.info { background: var(--brand-muted); border: 1px solid var(--border); color: var(--muted-ink); }
section[data-testid="stSidebar"] .stCaption { opacity: 0.68; }
section[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
/* ---- tabs styled like a mobile segmented control ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: var(--brand-muted); padding: 5px; border-radius: 999px;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    height: 40px; border-radius: 999px; padding: 0 20px; font-weight: 700;
    color: var(--muted-ink); transition: all .18s ease;
}
.stTabs [aria-selected="true"] {
    background: #fff !important; color: var(--brand) !important; box-shadow: var(--shadow-sm);
}
/* ---- primary button: gradient, glossy, tactile press ---- */
button[kind="primary"] {
    background: linear-gradient(135deg, var(--brand-2), var(--brand)) !important;
    border: none !important; border-radius: 999px !important;
    box-shadow: 0 10px 24px rgba(18,60,80,.28), inset 0 1px 0 rgba(255,255,255,.25) !important;
    font-weight: 800 !important; letter-spacing: 0.01em !important;
    transition: transform .12s ease, box-shadow .12s ease !important;
}
button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(18,60,80,.34), inset 0 1px 0 rgba(255,255,255,.3) !important; }
button[kind="primary"]:active { transform: translateY(0); }
div[data-testid="stForm"], .stApp [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: var(--radius-sm) !important;
}
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
        "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
        "heart": '<path d="M12 21s-7.5-4.6-10-9.3C0.5 8.4 2.3 5 5.7 5c1.9 0 3.3 1 4.3 2.4C11 6 12.4 5 14.3 5c3.4 0 5.2 3.4 3.7 6.7C19.5 16.4 12 21 12 21z"/>',
    }
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:-2px; display:inline-block; margin-right:4px;">{paths[name]}</svg>')


def render_sidebar():
    """
    Age/sex/jaundice/family ASD history are collected for the parent's own
    record, to hand to a clinician -- the deployed model doesn't use them.
    Only the 10 Q-CHAT-10 answers feed the score.
    """
    st.sidebar.markdown("### About your child")
    st.sidebar.caption("A few quick details — mostly for your own records.")
    age_months = st.sidebar.slider("Age (months)", min_value=18, max_value=36, value=24)
    sex        = st.sidebar.radio("Sex", ["Male", "Female"])
    jaundice    = st.sidebar.checkbox("Had jaundice as a newborn")
    family_asd  = st.sidebar.checkbox("A close family member is autistic")

    st.sidebar.caption(
        "These details don't change the result below — the model looks "
        "only at the 10 questionnaire answers. We still keep them on "
        "screen so you have a complete record to share with a clinician."
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Local calibration")
    with st.sidebar.expander("How Lesotho health data shapes this tool", expanded=False):
        st.caption(
            "The deployment threshold is calibrated to real-world autism "
            "prevalence (Zeidan et al., 2022) and informed by Lesotho DHS "
            "2023-24 indicators. During development we also tested "
            "adjusting individual answers for stunting and anaemia, since "
            "both are common in young children here and can resemble "
            "autism traits on a few items. That adjustment was evaluated "
            "carefully — population-wide and individual-level, cross-"
            "validated — and didn't improve accuracy enough to justify "
            "shipping it, so it isn't part of the score you get below. "
            "See the About tab for the full comparison."
        )

    return age_months, sex, jaundice, family_asd


def _bordered_container():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def render_qchat_form():
    st.subheader("Ten quick questions")
    st.caption(
        "Think about how your child typically behaves — not just today. "
        "Pick the answer that fits best; there's no wrong one."
    )

    responses = {}
    cols = st.columns(2)
    for i, (item_id, question) in enumerate(QCHAT_ITEMS):
        with cols[i % 2]:
            with _bordered_container():
                st.markdown(f"**{i + 1}.** {question}")
                responses[item_id] = st.selectbox(
                    label=f"Response for {item_id}",
                    options=list(RESPONSE_OPTIONS.keys()),
                    key=f"qchat_{item_id}",
                    label_visibility="collapsed",
                )
    answered = sum(1 for v in responses.values() if v)
    st.progress(answered / max(len(QCHAT_ITEMS), 1), text=f"{answered} of {len(QCHAT_ITEMS)} answered")
    return responses


def _risk_tier(prob: float):
    """
    Tier cutoffs for a PRIOR-CORRECTED probability, where the deployment
    ASD prevalence is calibrated to ~1% (Zeidan et al., 2022), not the
    ~42% training-set prevalence. Raw probabilities cluster near 0 after
    correction, so cutoffs are set relative to the model's own decision
    threshold rather than a fixed scale.
    """
    predictor = get_predictor()
    thr = getattr(predictor, "threshold", None) or 0.01
    if prob < thr:
        return "low", "LOOKS TYPICAL SO FAR", "#2E8B57"
    elif prob < thr * 3:
        return "mid", "WORTH KEEPING AN EYE ON", "#E2A33B"
    else:
        return "high", "TALK TO A CLINICIAN SOON", "#C1443A"


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
    needle_angle = -90 + (frac * 180)
    return f"""<svg viewBox="0 0 220 130" width="220" height="130" style="overflow:visible;">
    <defs>
        <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#2E8B57"/>
            <stop offset="50%" stop-color="#E2A33B"/>
            <stop offset="100%" stop-color="#C1443A"/>
        </linearGradient>
        <radialGradient id="hubGrad" cx="35%" cy="30%" r="75%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.9"/>
            <stop offset="100%" stop-color="#dfe9ee" stop-opacity="0.15"/>
        </radialGradient>
    </defs>
    <path d="M 20 110 A 90 90 0 0 1 200 110" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="14" stroke-linecap="round"/>
    <path d="M 20 110 A 90 90 0 0 1 200 110" fill="none" stroke="url(#gaugeGrad)" stroke-width="14"
          stroke-linecap="round" stroke-dasharray="{arc_len}" stroke-dashoffset="{offset}"
          style="transition: stroke-dashoffset 1s cubic-bezier(.22,1,.36,1);"/>
    <g transform="rotate({needle_angle} 110 110)" style="transition: transform 1s cubic-bezier(.22,1,.36,1);">
        <line x1="110" y1="110" x2="110" y2="34" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    </g>
    <circle cx="110" cy="110" r="9" fill="url(#hubGrad)" stroke="#fff" stroke-width="1.5"/>
    <text x="12" y="128" font-size="10" fill="rgba(255,255,255,.55)" font-family="Manrope, sans-serif">Typical</text>
    <text x="96" y="26" font-size="10" fill="rgba(255,255,255,.55)" font-family="Manrope, sans-serif">Watch</text>
    <text x="176" y="128" font-size="10" fill="rgba(255,255,255,.55)" font-family="Manrope, sans-serif">Refer</text>
    </svg>"""


def render_performance_chart():
    """
    Bar chart of this model's AUROC against published Q-CHAT-10 /
    autism-screening benchmarks, sourced from
    outputs/evaluation/benchmark_comparison.csv (produced by the
    notebook's benchmark comparison cell). Falls back gracefully if the
    file isn't present in the deployment bundle.
    """
    st.markdown("### How accurate is this, compared to other tools?")
    st.caption(
        "AUROC is a standard accuracy score from 0.5 (a coin flip) to 1.0 (perfect). "
        "Higher bars mean the tool is better at telling apart children who do and "
        "don't go on to receive an autism diagnosis."
    )

    fp = "outputs/evaluation/benchmark_comparison.csv"
    if not os.path.exists(fp):
        st.info(
            "Benchmark comparison data not found in this deployment. "
            "Copy outputs/evaluation/benchmark_comparison.csv from the "
            "notebook run into the app's outputs folder."
        )
        return

    df = pd.read_csv(fp)
    df["AUROC_numeric"] = pd.to_numeric(df["AUROC"], errors="coerce")
    df_plot = df.dropna(subset=["AUROC_numeric"]).copy()

    # Shorten labels for legibility in a horizontal bar chart.
    def short_label(m):
        m = str(m)
        if "this study" in m.lower():
            return "This study (Lesotho-calibrated)"
        return m.split("—")[0].strip() if "—" in m else m[:40]

    df_plot["label"] = df_plot["Model"].apply(short_label)
    df_plot = df_plot.sort_values("AUROC_numeric", ascending=True)

    is_this_study = df_plot["Model"].str.contains("this study", case=False, na=False)
    colours = ["#123C50" if flag else "#C7B896" for flag in is_this_study]

    fig, ax = plt.subplots(figsize=(7.5, max(2.5, 0.4 * len(df_plot))))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.barh(df_plot["label"], df_plot["AUROC_numeric"], color=colours)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("AUROC", color="gray", fontsize=9)
    ax.tick_params(colors="gray", labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Source: outputs/evaluation/benchmark_comparison.csv. Not every tool "
        "is directly comparable — they use different questions, populations, "
        "or signals (some also use video or eye-tracking). See the 'Directly "
        "comparable?' column in the underlying table, and the About tab, for "
        "caveats. Tools reported only as PPV/NPV (e.g. Canvas Dx) are left off "
        "this chart since they don't have a single AUROC figure."
    )


def render_capability_chart():
    st.markdown("### What each tool offers")
    st.caption("A side-by-side of features — this isn't about accuracy, just what you get.")

    capability_df = pd.DataFrame(
        {
            "This app": [1, 1, 1, 1, 1],
            "M-CHAT-R/F (generic use)": [0, 0, 0, 0, 1],
            "Q-CHAT-10 form only": [0, 1, 0, 0, 1],
        },
        index=[
            "Calibrated for this population",
            "Looks at behaviour + speech",
            "Explains each child's result",
            "Checked for fairness across groups",
            "Free and open to use",
        ],
    )

    show_df = capability_df.replace({1: "✓", 0: "—"}).T
    st.dataframe(show_df, use_container_width=True)


def render_results(result: dict, responses: dict):
    st.markdown("### Your result")

    prob = float(result.get("prob_calibrated", result.get("prob_fused", 0.0)))
    tier, tier_label, _ = _risk_tier(prob)
    thr = float(result.get("threshold", 0.5))

    banner_text = (
        "This pattern of answers is associated with a higher chance of autism-related traits. "
        "We'd recommend booking a developmental assessment with a clinician."
        if result.get("at_risk", False)
        else "Nothing here is flagging as an elevated risk right now. Keep watching your child's "
        "development, and check in again if anything changes."
    )
    st.markdown(
        f'<div class="risk-banner {tier}">{icon("info", 15)} {banner_text}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="gauge-card fade-in">
        <div class="gauge-svg-wrap">{render_gauge_svg(prob)}</div>
        <div class="gauge-readout">
            <div class="gauge-score">{_fmt_pct(prob)}</div>
            <div class="gauge-tier-label {tier}">{tier_label}</div>
            <div style="margin-top:9px;font-size:.83rem;color:rgba(255,255,255,.78);">
                Flag threshold for this model: {_fmt_pct(thr)}
            </div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.caption(
        "This number is scaled to how common autism actually is in the "
        "general population (about 1 in 100 children, Zeidan et al., 2022) — "
        "so even a 'talk to a clinician' result will look like a small "
        "percentage. What matters is where it sits above or below the "
        "threshold line, not whether it's close to 50%."
    )

    c1, c2 = st.columns(2)
    c1.metric("Overall result", _fmt_pct(prob))
    c2.metric("From behaviour answers", _fmt_pct(result.get("prob_behavioural", 0.0)))

    st.markdown(
        f'<div class="notice-box info">{icon("info", 15)} '
        f'This result is based only on your child\'s questionnaire answers, '
        f'with the flag threshold calibrated for real-world autism prevalence.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("How this result was calculated"):
        st.caption(result.get("validation_note", "Model details unavailable."))
        st.caption(f"Model version in use: {str(result.get('model_mode', 'unknown')).lower()}")

    notes = result.get("cultural_notes", {}) or {}
    if notes:
        st.markdown("#### A note on a couple of your answers")
        st.caption(
            "Some questions about speech can read differently depending on language "
            "and culture. These notes flag that — they don't change your score."
        )
        for item_id, payload in notes.items():
            st.markdown(
                f"""<div class="flag-card">
                <div class="flag-card-top">
                    <div class="flag-card-name">{item_id}: you answered "{payload.get("response","—")}"</div>
                    <span class="flag-pill">Worth knowing</span>
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
        f"""<div class="hero fade-in"><div class="hero-eyebrow">● Research prototype — not a diagnosis</div>
        <div class="badge-row"><span class="badge-chip">{icon("pin", 12)} Built for Lesotho</span>
        <span class="badge-chip">{icon("child", 12)} Ages 18–36 months</span>
        <span class="badge-chip">{icon("speech", 12)} Behaviour &amp; speech signals</span>
        <span class="badge-chip warn">{icon("warning", 12)} Screening only — not diagnostic</span></div>
        <div class="hero-title">A two-minute check-in on how your child is <em>growing and connecting</em></div>
        <p class="hero-sub">Answer 10 everyday questions about how your child plays, points, and talks. In about two minutes you'll get a clear, honest read on whether it's worth talking to a clinician — calibrated for children growing up here, not just overseas.</p>
        <div class="pill-row"><div class="pill"><div class="pill-num">1,601</div><div class="pill-label">Children in the training data</div></div>
        <div class="pill"><div class="pill-num">{auroc_txt}</div><div class="pill-label">Accuracy score (AUROC)</div></div>
        <div class="pill"><div class="pill-num">{thr_txt}</div><div class="pill-label">Flag threshold in use</div></div>
        <div class="pill"><div class="pill-num">{mode_txt}</div><div class="pill-label">Model version loaded</div></div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="stripe-bar"></div>', unsafe_allow_html=True)
    st.markdown("### What this is")
    st.markdown(
        """
This is a short screening questionnaire, not a lab test or a diagnosis. It uses the same trained model built and evaluated during this project, so what you see here is exactly what was measured.

It scores your answers to the Q-CHAT-10 questionnaire using a behavioural ensemble, then rescales the result to how common autism actually is here rather than a lab's mix of cases. The goal is simple: help you decide, in two minutes, whether a longer conversation with a clinician is worth having sooner rather than later.

The model was trained on behavioural screening data from children in New Zealand, Saudi Arabia, and Poland, then its flag threshold was calibrated using real Lesotho health survey data and reviewed for fairness across different groups of children, so it doesn't quietly work better for some families than others.

**Worth remembering:** this tool cannot diagnose autism, and it isn't a substitute for a paediatrician, psychologist, or other qualified clinician. If anything here concerns you, please follow up with one.
        """
    )

    st.markdown("### At a glance")
    st.markdown(
        """<div class="exec-grid"><div class="exec-card"><div class="exec-card-title">What it does</div>
        <div class="exec-card-body">Reads your 10 answers, scales the result to real-world autism prevalence, and hands back a plain 'watch' or 'refer' recommendation.</div></div>
        <div class="exec-card"><div class="exec-card-title">Where the data comes from</div>
        <div class="exec-card-body">Toddler screening data from three countries, with the flag threshold tuned using Lesotho DHS health indicators and a review of local language and culture.</div></div>
        <div class="exec-card"><div class="exec-card-title">Who it's for</div>
        <div class="exec-card-body">Parents, caregivers, and front-line health workers who want a first read before booking a specialist.</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Why it's built differently")
    st.markdown(
        """<div class="unique-grid"><div class="unique-card"><span class="unique-num">Local fit</span><div class="unique-title">Calibrated for here, not just there</div><div class="unique-body">The result threshold is tuned to real-world autism rates (Zeidan et al., 2022) rather than borrowed wholesale from one overseas study.</div></div>
        <div class="unique-card"><span class="unique-num">Health context</span><div class="unique-title">Tested against common local health factors</div><div class="unique-body">We tested adjusting scores for Lesotho's stunting and anaemia rates, since both can look like autism traits on a few questionnaire items. It didn't improve accuracy enough to ship, so the deployed model doesn't include it — see the About tab.</div></div>
        <div class="unique-card"><span class="unique-num">Fairness</span><div class="unique-title">Checked across groups of children</div><div class="unique-body">We measured whether the tool works as well for different ages and sexes, and say plainly where it doesn't.</div></div>
        <div class="unique-card"><span class="unique-num">Language</span><div class="unique-title">Aware of how questions land</div><div class="unique-body">Speech-related questions carry a note where language or culture could change how you'd answer.</div></div></div>""",
        unsafe_allow_html=True,
    )

    render_performance_chart()
    render_capability_chart()

    st.markdown("### What this can — and can't — do for you")
    st.markdown(
        f"""<div class="safety-grid"><div class="safety-col can"><div class="safety-head">{icon("check", 14)} It can</div>
        <div class="safety-item">• Flag when it's worth seeing a clinician sooner</div>
        <div class="safety-item">• Help you prioritise, if a wait list is long</div>
        <div class="safety-item">• Explain why a couple of your answers got a note</div></div>
        <div class="safety-col cant"><div class="safety-head">{icon("cross", 14)} It can't</div>
        <div class="safety-item">• Diagnose autism</div>
        <div class="safety-item">• Replace a specialist's assessment</div>
        <div class="safety-item">• Adjust for your specific child's health history</div>
        <div class="safety-item">• Guarantee any particular outcome</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="cta-banner">
        <div>
            <div class="cta-text">Ready to check in?</div>
            <div class="cta-sub">Open the Screening tab above — it takes about two minutes.</div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_about():
    st.markdown("#### How it works, step by step")
    left, right = st.columns(2)

    with left:
        steps = [
            ("Step 1", "You answer the 10 Q-CHAT-10 questions"),
            ("Step 2", "A behavioural ensemble (XGBoost + Logistic Regression) scores your answers"),
            ("Step 3", "The result is rescaled to match real-world autism rates (Zeidan et al., 2022)"),
            ("Step 4", "You get a result, a recommendation, and notes on specific answers"),
        ]
        for num, text in steps:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-num">{num}</div>
                <div class="step-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption(
            "Your child's age, sex, jaundice history, and family history are kept on "
            "screen for your records, but the model doesn't use them to score."
        )

    with right:
        st.markdown("#### Where the data comes from")
        sources = [
            ("Training data",
             "1,601 Q-CHAT-10 screening records for children aged 18–36 months, from "
             "New Zealand, Saudi Arabia, and Poland."),
            ("Test data",
             "A separate Polish clinical dataset (Niedźwiecka et al., 2020) with 252 "
             "confirmed autism and typically-developing cases, never seen during training."),
            ("Threshold calibration",
             "Lesotho Demographic and Health Survey 2023–24 (LSKR81DT) — population-wide "
             "stunting and anaemia rates, and real-world autism prevalence."),
            ("Real-world prevalence",
             "A global pooled autism prevalence estimate (Zeidan et al., 2022), since the "
             "Lesotho DHS doesn't measure autism directly."),
            ("Language and culture check",
             "SADiLaR Sesotho sa Leboa child speech corpus — real therapist-child "
             "recordings, used to review how speech-related questions come across."),
            ("Benchmark comparison",
             "Published accuracy figures from Sollis et al. (2024, 2025), Rajagopalan et al. "
             "(2024), Perochon et al. (2023), and Canvas Dx, used in the Overview chart."),
        ]
        for title, body in sources:
            st.markdown(f"""
            <div class="source-block">
                <div class="source-title">{title}</div>
                <div class="source-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### The comorbidity adjustment we tried, and didn't ship")
    st.markdown("""
    <div class="context-box">
        Stunting and anaemia are common in young children in Lesotho, and both can look
        like autism traits on a few Q-CHAT-10 items. We tested reweighting item scores
        for this at two levels: a population-wide sensitivity test, and an individual-level
        version cross-validated on held-out data. Neither improved AUROC enough to justify
        the added complexity, so this deployed model scores Q-CHAT-10 answers alone. The
        analysis is documented as a negative result rather than left out quietly.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Where this tool falls short")
    st.markdown("""
    <div class="limit-box">
        This is a screening tool, not a diagnosis — treat a "talk to a clinician" result as
        a nudge to follow up, not a verdict. It hasn't yet been tested directly with children
        or caregivers in Lesotho. The speech corpus used for language review is in Sesotho sa
        Leboa, a close relative of Sesotho as spoken in Lesotho but not identical to it.
    </div>
    """, unsafe_allow_html=True)


def render_fairness():
    st.markdown("### Does it work equally well for every child?")
    st.markdown(
        "We checked results separately by age and sex. A bar is flagged when that "
        "group's score falls more than 0.05 below the overall average — that's our "
        "line for 'this needs attention,' not a pass/fail grade."
    )

    fairness_path = "outputs/fairness/subgroup_results.csv"
    if os.path.exists(fairness_path):
        df = pd.read_csv(fairness_path)
        st.dataframe(df, use_container_width=True)

        overall_f1 = df["f1"].mean()
        fig, ax = plt.subplots(figsize=(7, 2.5))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        colours = ["#C1443A" if f < overall_f1 - 0.05 else "#123C50" for f in df["f1"]]
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
            "Fairness results will show up here once model evaluation has run."
        )


def main():
    tab_overview, tab_screen, tab_about, tab_fairness = st.tabs(
        ["Overview", "Screening", "About", "Fairness"]
    )

    with tab_overview:
        render_overview()

    with tab_screen:
        age_months, sex, jaundice, family_asd = render_sidebar()
        responses = render_qchat_form()

        if st.button("Get my result", type="primary", use_container_width=True):
            predictor = get_predictor()
            result = predictor.predict(
                responses=responses,
                age_months=age_months,
                sex=sex,
                jaundice=jaundice,
                family_asd=family_asd,
            )
            render_results(result, responses)

    with tab_about:
        render_about()

    with tab_fairness:
        render_fairness()


if __name__ == "__main__":
    main()