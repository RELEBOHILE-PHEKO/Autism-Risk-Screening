import os
import numpy as np
import joblib

# Directory containing all trained model artifacts
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Q-CHAT-10 screening questions displayed in the UI
QCHAT_ITEMS = [
    ("Q1",  "Does your child look at you when you call his/her name?"),
    ("Q2",  "How easy is it for you to get eye contact with your child?"),
    ("Q3",  "Does your child point to indicate that s/he wants something?"),
    ("Q4",  "Does your child point to share interest with you?"),
    ("Q5",  "Does your child pretend (e.g. care for dolls, talk on a phone)?"),
    ("Q6",  "Does your child follow where you're looking?"),
    ("Q7",  "If someone in the family is upset, does your child show signs of wanting to comfort them?"),
    ("Q8",  "Would you describe your child's first words as typical?"),
    ("Q9",  "Does your child use simple gestures (e.g. wave goodbye)?"),
    ("Q10", "Does your child stare at nothing with no apparent purpose?"),
]

# Response encoding used during model training
RESPONSE_OPTIONS = {
    "Always":    0,
    "Usually":   0,
    "Sometimes": 1,
    "Rarely":    1,
    "Never":     1,
}

# Reverse scoring for Q10 (staring behaviour)
RESPONSE_OPTIONS_Q10 = {
    "Always":    1,
    "Usually":   1,
    "Sometimes": 1,
    "Rarely":    0,
    "Never":     0,
}

# Items requiring reverse encoding
REVERSE_ITEMS = {"Q10"}

# Speech-related items used for cultural interpretation
SPEECH_ITEMS = {"Q1", "Q8", "Q9"}

# Cultural considerations identified through corpus analysis
CULTURAL_NOTES = {
    "Q1": "Response to name may be influenced by language and communication patterns in Sesotho-speaking contexts.",
    "Q8": "Early speech development can vary across languages and cultures. This item may not transfer directly to Sesotho linguistic norms.",
    "Q9": "Gestures and social behaviours may differ across cultural settings. Cultural alignment analysis flagged this item.",
}

class AutismPredictor:

    def __init__(self):
        # Model placeholders
        self.model_beh = None
        self.model_dem = None
        self.meta_model = None

        # DHS-calibrated decision threshold
        self.threshold = 0.5

        self.models_loaded = False
        self._load_models()

    def _load_models(self):
        # Load trained behavioural, demographic and fusion models
        try:
            self.model_beh = joblib.load(os.path.join(MODEL_DIR, "xgb_behavioural.joblib"))
            self.model_dem = joblib.load(os.path.join(MODEL_DIR, "xgb_demographic.joblib"))
            self.meta_model = joblib.load(os.path.join(MODEL_DIR, "meta_model.joblib"))

            # Prefer the enriched DHS-calibrated threshold (10 covariates:
            # stunting, anaemia, no_caregiver, rural, low_maternal_edu,
            # low_wealth, inadequate_anc, small_birth, home_delivery,
            # short_interval). Falls back to the basic 4-covariate threshold
            # if the enriched artifact isn't available.
            enriched_path = os.path.join(MODEL_DIR, "threshold_enriched.joblib")
            basic_path = os.path.join(MODEL_DIR, "threshold.joblib")
            threshold_path = enriched_path if os.path.exists(enriched_path) else basic_path
            self.threshold = float(joblib.load(threshold_path))

            self.models_loaded = True
        except FileNotFoundError:
            # Fall back to demo mode if model files are unavailable
            self.models_loaded = False

    @staticmethod
    def encode_responses(responses: dict) -> np.ndarray:
        # Convert questionnaire responses into binary model features
        scores = []

        for item_id, _ in QCHAT_ITEMS:
            raw = responses.get(item_id, "Sometimes")

            if item_id in REVERSE_ITEMS:
                scores.append(RESPONSE_OPTIONS_Q10.get(raw, 1))
            else:
                scores.append(RESPONSE_OPTIONS.get(raw, 1))

        return np.array(scores, dtype=float).reshape(1, -1)

    @staticmethod
    def encode_demographics(age_months: int, sex: str,
                             jaundice: bool = False, family_asd: bool = False) -> np.ndarray:
        # Encode demographics in the exact column order used during training:
        # DEM_COLS = ["age_years", "sex", "Jaundice", "Family_ASD"]
        return np.array([[
            age_months / 12.0,
            1 if sex == "Male" else 0,
            1 if jaundice else 0,
            1 if family_asd else 0,
        ]], dtype=float)

    @staticmethod
    def recalibrate_individual(prob: float, stunted: bool, anaemic: bool,
                               no_caregiver: bool, rural: bool,
                               low_maternal_edu: bool = False, low_wealth: bool = False,
                               inadequate_anc: bool = False, small_birth: bool = False,
                               home_delivery: bool = False, short_interval: bool = False) -> float:
        # DHS-based contextual risk adjustment.
        # Weights mirror the relative ordering of the enriched population-level
        # risk score from the training pipeline (stunting > anaemia/maternal
        # education/wealth > no_caregiver/rural > ANC/birth size > delivery/interval),
        # applied here per-child rather than as a single population-wide threshold shift.
        adjustment = sum([
            0.030 * stunted,
            0.020 * anaemic,
            0.020 * low_maternal_edu,
            0.020 * low_wealth,
            0.020 * no_caregiver,
            0.010 * rural,
            0.010 * inadequate_anc,
            0.010 * small_birth,
            0.005 * home_delivery,
            0.005 * short_interval,
        ])

        return float(np.clip(prob + adjustment, 0.0, 1.0))

    @staticmethod
    def get_cultural_notes(responses: dict) -> dict:
        # Return cultural notes for speech-related questions
        return {
            item_id: {
                "response": responses.get(item_id, "—"),
                "note": CULTURAL_NOTES[item_id],
            }
            for item_id in SPEECH_ITEMS
        }

    def predict(self, responses: dict, age_months: int, sex: str,
                stunted: bool = False, anaemic: bool = False,
                no_caregiver: bool = False, rural: bool = False,
                low_maternal_edu: bool = False, low_wealth: bool = False,
                inadequate_anc: bool = False, small_birth: bool = False,
                home_delivery: bool = False, short_interval: bool = False,
                jaundice: bool = False, family_asd: bool = False) -> dict:

        # Prepare behavioural and demographic inputs
        X_beh = self.encode_responses(responses)
        X_dem = self.encode_demographics(age_months, sex, jaundice, family_asd)

        if self.models_loaded:

            # Behavioural model prediction
            prob_beh = float(self.model_beh.predict_proba(X_beh)[0][1])

            # Demographic model prediction
            prob_dem = float(self.model_dem.predict_proba(X_dem)[0][1])

            # Late-fusion stacking using meta-model
            X_meta = np.array([[prob_beh, prob_dem]])
            prob_fused = float(self.meta_model.predict_proba(X_meta)[0][1])

            demo_mode = False

        else:
            # Simplified fallback prediction when models are missing
            prob_beh = float(np.clip(X_beh.sum() / 10.0, 0.0, 1.0))
            prob_dem = 0.30
            prob_fused = (prob_beh + prob_dem) / 2.0
            demo_mode = True

        # Apply DHS contextual calibration (10-indicator enriched set)
        prob_calibrated = self.recalibrate_individual(
            prob_fused, stunted, anaemic, no_caregiver, rural,
            low_maternal_edu, low_wealth, inadequate_anc,
            small_birth, home_delivery, short_interval,
        )

        return {
            "prob_behavioural": round(prob_beh, 4),
            "prob_demographic": round(prob_dem, 4),
            "prob_fused": round(prob_fused, 4),
            "prob_calibrated": round(prob_calibrated, 4),
            "threshold": round(self.threshold, 4),
            "at_risk": bool(prob_calibrated >= self.threshold),
            "cultural_notes": self.get_cultural_notes(responses),
            "validation_note": (
                "Trained on Q-CHAT-10 data (NZ + Saudi Arabia, n=1,601). "
                "Tested on Polish clinical dataset (n=252). "
                "AUROC = 0.814. Threshold calibrated using Lesotho DHS 2023-24 "
                "(enriched, 10-indicator model)."
            ),
            "demo_mode": demo_mode,
        }

# Singleton instance prevents repeated model loading
_instance: AutismPredictor | None = None

def get_predictor() -> AutismPredictor:
    global _instance

    if _instance is None:
        _instance = AutismPredictor()

    return _instance

# Local test run
if __name__ == "__main__":
    result = AutismPredictor().predict(
        responses={
            "Q1": "Rarely",
            "Q2": "Sometimes",
            "Q3": "Never",
            "Q4": "Never",
            "Q5": "Sometimes",
            "Q6": "Sometimes",
            "Q7": "Rarely",
            "Q8": "Rarely",
            "Q9": "Sometimes",
            "Q10": "Always",
        },
        age_months=24,
        sex="Male",
        stunted=True,
        anaemic=True,
        no_caregiver=False,
        rural=True,
    )