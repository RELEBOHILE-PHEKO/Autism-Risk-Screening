# Cross-Dataset Evaluation of Machine-Learning Autism Risk Screening with Fairness Analysis for a Lesotho Context
 ## Lesedi Lens 

 app url :https://lesedi-lensvercelapp-rust.vercel.app/

 
 demo video: 

Lesedi Lens is a caregiver-facing Q-CHAT-10 autism screening prototype for
children aged 18–36 months. The current implementation follows the notebook's
production pipeline: a behavioural XGBoost + logistic regression ensemble,
calibrated with Saerens prior correction and deployed via a FastAPI backend.

**Notebook-aligned deployment output:** AUROC 0.892 on the held-out deployment
configuration, using the deploy_* model artifacts in the models folder.

---

## Repository layout

```text
backend/                  # FastAPI inference service
  api.py                  # Loads the deploy_* model artifacts and serves /predict
  requirements.txt
Frontend/                 # Next.js user interface
  app/                    # Pages and global layout
  components/             # Lens UI modules and cards
  lib/                    # API client and shared helpers
  package.json
models/                   # Notebook-trained deployment artifacts
  deploy_xgb_behavioural.joblib
  deploy_lr_behavioural.joblib
  deploy_blend_weight.joblib
  deploy_prior_correction.joblib
  deploy_threshold.joblib
notebook/                  # Training and evaluation notebook
  Autism_Screening_pipeline.ipynb
outputs/                  # Evaluation, fairness, and alignment exports
requirements.txt          # Python dependencies for the notebook + backend runtime
```

---

## What matches the notebook

The current app is aligned with the notebook's production configuration:

- The backend loads the notebook's deploy_* artifacts from the models folder.
- The prediction logic uses the same blend-weight ensemble and Saerens
  prior-correction step described in the notebook.
- The frontend displays the deployment-oriented metrics and thresholds that
  correspond to the notebook's reported AUROC of 0.892.

If you need to reproduce the notebook environment, the Python dependencies in
requirements.txt are the relevant starting point.

---

## Local setup

### 1. Create and activate a Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 3. Install frontend dependencies

```bash
cd Frontend
npm install
```

---

## Run the app locally

Open two terminals.

### Terminal 1 — backend API

```bash
cd <repo-folder>
.venv\Scripts\activate
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

The API health check is available at:

```text
http://127.0.0.1:8000/health
```

### Terminal 2 — frontend UI

```bash
cd <repo-folder>\Frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

If you need to point the frontend at a different backend URL, create a local
environment file in Frontend and set NEXT_PUBLIC_API_URL.

---

## Deploy to Vercel and Render

### Frontend on Vercel

1. Push this repository to GitHub.
2. In Vercel, click New Project and import the repository.
3. Set the Vercel Root Directory to Frontend.
4. Vercel will detect the Next.js app automatically.
5. Add this environment variable in Vercel:

```text
NEXT_PUBLIC_API_URL=https://your-render-service-name.onrender.com
```

6. Deploy the project.

### Backend on Render

1. In Render, create a New Web Service from the same GitHub repository.
2. Choose the repository and keep the root directory as the repo root.
3. Use these settings:

```text
Build Command: pip install -r backend/requirements.txt
Start Command: uvicorn backend.api:app --host 0.0.0.0 --port $PORT
```

4. Deploy the service.
5. Copy the Render URL and paste it into the Vercel environment variable above.

This setup keeps the UI on Vercel and the FastAPI prediction service on Render.

---

## Project capabilities

- Screening tab: answer the 10 Q-CHAT-10 questions and receive a calibrated
  risk result plus a clinician-friendly summary.
- Overview tab: high-level project summary, benchmark comparison, and feature
  highlights.
- About tab: methodology, data sources, and stated limitations.
- Fairness tab: subgroup audit views for age and sex.

---

## Notes and limitations

This is a research prototype, not a diagnostic tool. It is intended for
educational and planning purposes and should be reviewed by qualified clinical
or public-health stakeholders before any field deployment.
