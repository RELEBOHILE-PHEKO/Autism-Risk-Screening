# Autism Risk Screening in Southern  African Children Using Multimodal AI
-------
video link: https://youtu.be/l2zPPSuSnXA

Deployed URL- https://autism-risk-screening.streamlit.app/

-------


Research prototype for early autism risk screening in young children using a multimodal pipeline built around Q-CHAT-10 responses, demographic features, Lesotho DHS contextual calibration, and a local SADiLaR speech-corpus audit.

> This project is for research and demonstration only. It is not a clinical diagnostic tool.

## What is in this repo

- `notebook/autism_screening_pipeline .ipynb` contains the full training and analysis workflow.
- `app/app.py` is a Streamlit screening app.
- `app/predictor.py` loads the trained models and performs inference.
- `data/raw/` contains the local datasets used by the notebook.
- `models/` stores the saved `joblib` models and threshold artifact.
- `outputs/` stores generated charts and audit reports.

## Current pipeline

The notebook currently does the following:

1. Loads the unified Q-CHAT training dataset from `data/raw/qchat/Autusim_DATA_Clean_Encoded.xlsx`.
2. Loads the Polish test dataset from `data/raw/qchat/QCHAT_dataset2 mendeley.sav` when available.
3. Trains two XGBoost models:
   - behavioural model from the 10 Q-CHAT items
   - demographic model from age and sex
4. Combines the two models with late fusion.
5. Recalibrates the decision threshold using the local DHS CSV at `data/raw/dhs/LSKR81FL.csv`.
6. Runs a SADiLaR speech-corpus audit from `data/raw/SADiLaR/`.
7. Acoustic Feature extraction
8. Produces fairness and evaluation outputs under `outputs/`.
9. Saves trained artifacts to `models/`.

SHAP is treated as optional. If the local environment cannot import it cleanly, the notebook skips explainability instead of failing.

## Repository layout

```text
.
├── app/
│   ├── app.py
│   └── predictor.py
├── data/
│   ├── raw/
│   │   ├── qchat/
│   │   │   ├── Autusim_DATA_Clean_Encoded.xlsx
│   │   │   └── QCHAT_dataset2 mendeley.sav
│   │   ├── dhs/
│   │   │   ├── LSKR81FL.csv
│   │   │   ├── LSKR81FL.DTA
│   │   │   ├── LSKR81FL.DCT
│   │   │   ├── LSKR81FL.DO
│   │   │   ├── LSKR81FL.FRQ
│   │   │   ├── LSKR81FL.FRW
│   │   │   ├── LSKR81FL.MAP
│   │   │   └── LSKR81FL_v14.dta
│   │   └── SADiLaR/
│           ├── Sesotho sa Leboa - Orthographic Transcriptions/
│           └── Sesotho sa Leboa Recordings/
│   
├── models/
├── notebook/
│   └── autism_screening_pipeline.ipynb
├── outputs/
│   ├── alignment/
│   ├── evaluation/
│   └── fairness/
├── README.md
└── requirements.txt
```

## Data inventory

### Q-CHAT data

- `data/raw/qchat/Autusim_DATA_Clean_Encoded.xlsx`
- `data/raw/qchat/QCHAT_dataset2 mendeley.sav`

### DHS data

The DHS folder contains the original export artifacts plus the converted CSV used by the notebook:

- `data/raw/dhs/LSKR81FL.csv`
- `data/raw/dhs/LSKR81FL.DTA`
- `data/raw/dhs/LSKR81FL.DCT`
- `data/raw/dhs/LSKR81FL.DO`
- `data/raw/dhs/LSKR81FL.FRQ`
- `data/raw/dhs/LSKR81FL.FRW`
- `data/raw/dhs/LSKR81FL.MAP`
- `data/raw/dhs/LSKR81FL_v14.dta`

### SADiLaR speech corpus

The SADiLaR folder contains paired speech transcripts and recordings in Sesotho sa Leboa:

- `data/raw/SADiLaR/Sesotho sa Leboa - Orthographic Transcriptions/*.eaf`
- `data/raw/SADiLaR/Sesotho sa Leboa Recordings/*.WAV`

The notebook currently audits the local corpus and reports missing transcript/audio pairs before any downstream speech analysis.

## Outputs already generated

The repo already includes notebook outputs from recent runs:

- `outputs/evaluation/eda_overview.png`
- `outputs/evaluation/correlation_matrix.png`
- `outputs/evaluation/qchat_heatmap.png`
- `outputs/evaluation/roc_and_cm.png`
- `outputs/fairness/subgroup_results.csv`
- `outputs/fairness/fairness_f1.png`
- `outputs/alignment/sadilar_manifest.csv`
- `outputs/alignment/sadilar_audit.png`
- `outputs/alignment/alignment_scores.csv`
- `outputs/alignment/alignment_chart.png`

## Trained models

Saved model artifacts are already present in `models/`:

- `models/xgb_behavioural.joblib`
- `models/xgb_demographic.joblib`
- `models/threshold.joblib`
- `meta_model.joblib`
  
## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

The project currently depends on:

- pandas
- numpy
- scikit-learn
- xgboost
- shap
- librosa
- imbalanced-learn
- matplotlib
- seaborn
- pyreadstat
- streamlit
- joblib

## Run the notebook

Open the notebook in VS Code or Jupyter:

```bash
jupyter notebook "notebook/autism_screening_pipeline .ipynb"
```

Or open it directly in VS Code and run the cells in order.

## Run the Streamlit app

```bash
streamlit run app/app.py
```

The app uses the saved models in `models/`. If the models are missing, it falls back to a demo mode rather than crashing.

## Notes

- The notebook uses the local DHS CSV first and only falls back to the local `.dta` if needed.
- The local SADiLaR corpus is partially paired: 37 transcripts and 31 recordings, with 6 transcripts currently missing audio matches.
- The project is a screening prototype, not a diagnostic device.

## License and ethics

No license file is present in the repo. Treat the code and data as research material only, and follow the relevant data-use restrictions for DHS, Q-CHAT, and SADiLaR assets.
