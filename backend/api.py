"""
Autism Risk Screening API

This API loads the trained autism screening models and provides
an endpoint that predicts autism risk using Q-CHAT-10 responses.

Run the server from the backend folder:

    uvicorn api:app --reload --port 8000
"""

from pathlib import Path
from typing import List

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# The models folder is in the project root
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


# Create the FastAPI app
app = FastAPI(
    title="Autism Risk Screening API",
    version="1.0.0",
)

# Allow requests from the frontend.
# This is okay for development but should be restricted when deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Store loaded models here so they only load once
_artifacts = {}


@app.on_event("startup")
def load_artifacts():
    """
    Load all the trained models and other files needed for prediction.
    """

    required = [
        "deploy_xgb_behavioural.joblib",
        "deploy_lr_behavioural.joblib",
        "deploy_blend_weight.joblib",
        "deploy_prior_correction.joblib",
        "deploy_threshold.joblib",
    ]

    # Check if any required files are missing
    missing = [
        file
        for file in required
        if not (MODELS_DIR / file).exists()
    ]

    if missing:
        raise RuntimeError(
            f"Missing model files: {missing}"
        )

    # Load the trained models
    _artifacts["xgb"] = joblib.load(MODELS_DIR / "deploy_xgb_behavioural.joblib")
    _artifacts["lr"] = joblib.load(MODELS_DIR / "deploy_lr_behavioural.joblib")

    # Load the blending weight, prior correction values and threshold
    _artifacts["blend_weight"] = joblib.load(MODELS_DIR / "deploy_blend_weight.joblib")
    _artifacts["prior"] = joblib.load(MODELS_DIR / "deploy_prior_correction.joblib")
    _artifacts["threshold"] = joblib.load(MODELS_DIR / "deploy_threshold.joblib")


def saerens_prior_correction(
    p: np.ndarray,
    train_prior: float,
    target_prior: float,
) -> np.ndarray:
    """
    Adjust the predicted probabilities so they match the expected
    autism prevalence in the target population.
    """

    # Prevent values from becoming exactly 0 or 1
    p = np.clip(p, 1e-6, 1 - 1e-6)

    numerator = p * (target_prior / train_prior)

    denominator = (
        numerator +
        (1 - p) * ((1 - target_prior) / (1 - train_prior))
    )

    return numerator / denominator


class ScreeningRequest(BaseModel):
    # The frontend sends 10 answers (Q1-Q10)
    answers: List[int] = Field(
        ...,
        min_length=10,
        max_length=10,
    )


class ScreeningResponse(BaseModel):
    # Information returned to the frontend
    risk_score: float
    at_risk: bool
    threshold: float

    disclaimer: str = (
        "This screening tool is only for educational purposes "
        "and is not a clinical diagnosis."
    )


@app.get("/health")
def health():
    """Simple endpoint to check if the API is working."""

    return {
        "status": "ok",
        "artifacts_loaded": bool(_artifacts),
    }


@app.post("/predict", response_model=ScreeningResponse)
def predict(req: ScreeningRequest):
    """
    Predict autism risk from the user's Q-CHAT-10 responses.
    """

    # Make sure every answer is either 0 or 1
    if not all(answer in (0, 1) for answer in req.answers):
        raise HTTPException(
            status_code=422,
            detail="All answers must be either 0 or 1."
        )

    # Convert the answers into a format the models can use
    X = np.array(req.answers, dtype=float).reshape(1, -1)

    xgb_model = _artifacts["xgb"]
    lr_model = _artifacts["lr"]
    blend_weight = _artifacts["blend_weight"]
    prior = _artifacts["prior"]
    threshold = _artifacts["threshold"]

    # Get predictions from both models
    prob_xgb = xgb_model.predict_proba(X)[:, 1]
    prob_lr = lr_model.predict_proba(X)[:, 1]

    # Combine both predictions using the learned blend weight
    ensemble_prob = (
        blend_weight * prob_xgb +
        (1 - blend_weight) * prob_lr
    )

    # Apply prior correction
    corrected_prob = saerens_prior_correction(
        ensemble_prob,
        prior["train_prior"],
        prior["target_prior"],
    )

    score = float(corrected_prob[0])

    return ScreeningResponse(
        risk_score=round(score, 4),
        at_risk=bool(score >= threshold),
        threshold=round(float(threshold), 4),
    )