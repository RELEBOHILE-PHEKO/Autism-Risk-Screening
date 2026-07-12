# Autism Risk Screening — Lesotho-Calibrated

A caregiver-facing Q-CHAT-10 autism screening tool, built with a behavioural
ensemble model (XGBoost + Logistic Regression), calibrated to real-world ASD
prevalence, and adjusted using Lesotho DHS 2023–24 population health data
(stunting and anaemia prevalence).

**Final model AUROC: 0.892** — beats the published Sollis et al. (2025)
benchmark (0.870) on the identical NZ+Saudi→Poland Q-CHAT-10 transfer setup.

---

## Links

- **Deployed app:** https://autism-screening.streamlit.app/
- **Demo video (5 min):**https://youtu.be/OBL_Xl2qud8

---

## What's in this repo

```
├── app.py                          # Streamlit application (UI)
├── predictor.py                    # Model loading + inference logic
├── requirements.txt                # Python dependencies
├── autism_screening_pipeline.ipynb # Full training/evaluation notebook
├── models/                         # Saved trained model artifacts
│   ├── final_xgb_behavioural.joblib
│   ├── final_lr_behavioural.joblib
│   ├── final_blend_weight.joblib
│   ├── final_prior_correction.joblib
│   ├── final_threshold.joblib
│   └── final_dhs_comorbidity_params.joblib
├── data/raw/qchat/                 # Q-CHAT-10 training datasets
├── data/raw/dhs/                   # Lesotho DHS 2023-24 microdata (KR, BR)
└── outputs/
    ├── evaluation/                 # Ablation study, benchmark comparison
    └── fairness/                   # Subgroup fairness results
```

---

## How to install and run (step by step)

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd <repo-folder>
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
streamlit run app.py
```

**5. Open in your browser**

Streamlit will open automatically, or visit `http://localhost:8501`.

---

## Core functionality

- **Screening tab:** answer 10 Q-CHAT-10 behavioural questions, get a
  calibrated risk score, referral recommendation, and cultural interpretation
  notes on speech-related items.
- **Overview tab:** project summary, benchmark comparison chart against
  published autism screening tools, capability comparison.
- **About tab:** full methodology, data sources, and stated limitations.
- **Fairness tab:** subgroup performance evaluation (age, sex).

---

## Key technical contributions

1. **Behavioural ensemble** (XGBoost + Logistic Regression), CV-blended,
   trained on Q-CHAT-10 items only — outperforms models that include weak
   demographic signal (age/sex/jaundice/family history, AUROC ~0.61 alone).
2. **Population-prevalence prior correction** (Saerens et al., 2002) —
   rescales model output to match real-world ASD prevalence (~1%, Zeidan
   et al., 2022) instead of the training data's enriched ~42% rate.
3. **DHS comorbidity adjustment** — reweights Q-CHAT-10 items using real
   Lesotho DHS 2023–24 stunting (50.1%) and anaemia (62.6%) prevalence
   among children 18–36 months, since these conditions can mimic
   autism-related behaviours on screening items.
4. **Fairness evaluation** across sex and age subgroups.
5. **Cultural alignment review** of speech-related items against the
   SADiLaR Sesotho sa Leboa child speech corpus.

---

## Limitations

This is a research prototype, not a diagnostic tool. It has not been
validated with children or caregivers in Lesotho. The DHS comorbidity
adjustment is a population-level correction only; an individual-level
version was tested and found to underperform due to the absence of
Lesotho data linking individual Q-CHAT-10 responses to health records.
