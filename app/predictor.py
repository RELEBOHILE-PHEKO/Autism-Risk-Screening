import os
import numpy as np
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

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

RESPONSE_OPTIONS = {"Always": 0, "Usually": 1, "Sometimes": 2, "Rarely": 3, "Never": 4}
REVERSE_ITEMS    = {"Q10"}
SPEECH_ITEMS     = {"Q1", "Q8", "Q9"}

CULTURAL_NOTES = {
    "Q1": "Response to name may be influenced by language and communication patterns.",
    "Q8": "Early speech development can vary across languages and cultures.",
    "Q9": "Gestures and social behaviours may differ across cultural settings.",
}


# Handles model loading and prediction
class AutismPredictor:

    def __init__(self):
        self.model_beh = None
        self.model_dem = None
        self.threshold = 0.5
        self.models_loaded = False
        self._load_models()

    # Load saved models and threshold
    def _load_models(self):
        try:
            self.model_beh = joblib.load(os.path.join(MODEL_DIR, "xgb_behavioural.joblib"))
            self.model_dem = joblib.load(os.path.join(MODEL_DIR, "xgb_demographic.joblib"))
            self.threshold = float(joblib.load(os.path.join(MODEL_DIR, "threshold.joblib")))
            self.models_loaded = True
        except FileNotFoundError:
            self.models_loaded = False

    # Convert questionnaire responses into model features
    @staticmethod
    def encode_responses(responses: dict) -> np.ndarray:
        scores = []
        for item_id, _ in QCHAT_ITEMS:
            s = RESPONSE_OPTIONS.get(responses.get(item_id, "Sometimes"), 2)
            scores.append(4 - s if item_id in REVERSE_ITEMS else s)
        return np.array(scores, dtype=float).reshape(1, -1)

    # Convert demographic information into numerical values
    # Note: sex encoding matches training — Male=1, Female=0
    @staticmethod
    def encode_demographics(age_months: int, sex: str) -> np.ndarray:
        return np.array([[
            age_months / 12.0,
            1 if sex == "Male" else 0,
        ]], dtype=float)

    # Adjust probability using contextual indicators
    @staticmethod
    def recalibrate_individual(prob: float, stunted: bool, anaemic: bool,
                               no_caregiver: bool, rural: bool) -> float:
        adjustment = sum([
            0.03 * stunted,
            0.02 * anaemic,
            0.02 * no_caregiver,
            0.01 * rural,
        ])
        return float(np.clip(prob + adjustment, 0.0, 1.0))

    # Return interpretation notes for speech-related questions
    @staticmethod
    def get_cultural_notes(responses: dict) -> dict:
        return {
            item_id: {
                "response": responses.get(item_id, "—"),
                "note": CULTURAL_NOTES[item_id],
            }
            for item_id in SPEECH_ITEMS
        }

    # Generate autism risk prediction
    def predict(self, responses: dict, age_months: int, sex: str,
                stunted: bool = False, anaemic: bool = False,
                no_caregiver: bool = False, rural: bool = False) -> dict:

        X_beh = self.encode_responses(responses)
        X_dem = self.encode_demographics(age_months, sex)

        if self.models_loaded:
            prob_beh  = float(self.model_beh.predict_proba(X_beh)[0][1])
            prob_dem  = float(self.model_dem.predict_proba(X_dem)[0][1])
            demo_mode = False
        else:
            prob_beh  = float(np.clip(X_beh.sum() / 28.0, 0.0, 1.0))
            prob_dem  = 0.30
            demo_mode = True

        prob_fused      = (prob_beh + prob_dem) / 2.0
        prob_calibrated = self.recalibrate_individual(
            prob_fused, stunted, anaemic, no_caregiver, rural
        )

        return {
            "prob_behavioural": round(prob_beh, 4),
            "prob_demographic": round(prob_dem, 4),
            "prob_fused":       round(prob_fused, 4),
            "prob_calibrated":  round(prob_calibrated, 4),
            "threshold":        round(self.threshold, 4),
            "at_risk":          bool(prob_calibrated >= self.threshold),
            "cultural_notes":   self.get_cultural_notes(responses),
            "validation_note":   "Models were trained on the unified Q-CHAT dataset and tested on the Polish clinical dataset when available.",
            "demo_mode":        demo_mode,
        }


# Cached predictor instance
_instance: AutismPredictor | None = None

# Return a shared predictor instance
def get_predictor() -> AutismPredictor:
    global _instance
    if _instance is None:
        _instance = AutismPredictor()
    return _instance


# Run a simple test when executing this file directly
if __name__ == "__main__":
    result = AutismPredictor().predict(
        responses={
            "Q1": "Rarely", "Q2": "Sometimes", "Q3":  "Never",
            "Q4": "Never",  "Q5": "Sometimes",  "Q6":  "Sometimes",
            "Q7": "Rarely", "Q8": "Rarely",     "Q9":  "Sometimes",
            "Q10": "Always",
        },
        age_months=24, sex="Male",
        stunted=True, anaemic=True, no_caregiver=False, rural=True,
    )

    for k, v in result.items():
        if k != "cultural_notes":
            print(f"{k}: {v}")

    print("\nCultural notes:")
    for item, info in result["cultural_notes"].items():
        print(f"  {item}: {info['response']}")