# Lesedi Lens: Autism Risk Screening

Lesedi Lens is a research prototype for caregiver-facing Q-CHAT-10 autism-risk screening for children aged 18–36 months in a Lesotho context. It combines a Next.js frontend with a FastAPI service that serves the pre-trained behavioural ensemble in `models/`.

> This is an educational screening prototype, not a diagnostic or clinical decision tool.

## What is included

```text
backend/                  FastAPI prediction service
Frontend/                 Next.js web interface
data/raw/qchat/           Q-CHAT source and external test datasets
models/                   Pre-trained deployment model artifacts
notebook/                 Training and evaluation notebook
outputs/                  Saved evaluation, fairness, and alignment results
```

The live application uses the `deploy_*.joblib` files in `models/`; it does not need the notebook to run.

## Requirements

- Python 3.11 (the deployment configuration uses Python 3.11.9)
- Node.js 20 or newer and npm
- The repository's `models/` directory, including all five `deploy_*.joblib` files

## Run locally

Clone the repository, then open two terminals in the repository root.

### 1. Set up Python and start the API

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

If PowerShell does not allow activation, use the virtual environment's executables directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Confirm the API is ready at `http://127.0.0.1:8000/health`. A successful response is:

```json
{"status":"ok","artifacts_loaded":true}
```

### 2. Start the frontend

In a second terminal:

```powershell
cd Frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open `http://127.0.0.1:3000` in a browser. The frontend defaults to `http://localhost:8000` for the API, which works with the local backend above.

To use another API address, create `Frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=https://your-api.example.com
```

Restart the frontend after changing this value.

## API input and output

`POST /predict` expects exactly ten binary Q-CHAT flags, ordered Q1 through Q10:

```json
{"answers":[0,0,0,0,0,0,0,0,0,0]}
```

Each value must be `0` or `1`. The API returns a Saerens prior-corrected risk score, the deployment threshold, and whether the score meets that threshold:

```json
{
  "risk_score": 0.0009,
  "at_risk": false,
  "threshold": 0.005,
  "disclaimer": "This screening tool is only for educational purposes and is not a clinical diagnosis."
}
```

## Notebook and research outputs

The notebook is named [autism_screening_Pipeline .ipynb](notebook/autism_screening_Pipeline%20.ipynb). It contains model training and evaluation and can take substantially longer than starting the app.

The bundled Q-CHAT files are sufficient for the core Q-CHAT workflow. Full notebook reproduction also requires the optional, untracked source datasets below:

- `data/raw/dhs/` for the Lesotho DHS calibration sections.
- `data/raw/SADiLaR/` for the language-alignment sections.

The checked-in CSV files under `outputs/` are the saved evaluation artifacts. They can be inspected without rerunning the notebook.

## Validation commands

After installing dependencies:

```powershell
# API health check (with the API running)
Invoke-RestMethod http://127.0.0.1:8000/health

# Frontend production build
cd Frontend
npm run build
```

The frontend imports Google Fonts at build time, so its build requires internet access. The current `npm run lint` script also requires ESLint to be installed; ESLint is not presently listed in the frontend development dependencies.

## Deployment

`render.yaml` deploys the FastAPI backend to Render from the repository root. For Vercel, import the repository and set the project root directory to `Frontend`, then configure:

```text
NEXT_PUBLIC_API_URL=https://your-render-service-name.onrender.com
```

The root `vercel.json` is also configured to install and build the `Frontend` application.

## Project links

- App: https://lesedi-lensvercelapp-rust.vercel.app/
- API: https://autism-risk-screening.onrender.com/
- Demo: https://youtu.be/lZQlUJxvguA
