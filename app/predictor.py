import os
import numpy as np
import joblib
import pandas as pd

# Directory containing all trained model artifacts
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "evaluation")

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
        self.model_beh = None
        self.model_lr = None
        self.model_dem = None
        self.meta_model = None

        self.threshold = 0.5
        self.blend_weight = 1.0
        self.train_prior = None
        self.target_prior = None
        self.dhs_params = {"item_weights": {}, "pop_stunting": 0.0, "pop_anaemia": 0.0}

        self.models_loaded = False
        self.model_mode = "demo"  # final | deploy | legacy | demo
        self.reference_auroc = None

        self._load_models()
        self._load_reference_metrics()

    def _load_reference_metrics(self):
        fp = os.path.join(OUTPUT_DIR, "benchmark_comparison.csv")
        if not os.path.exists(fp):
            return
        try:
            df = pd.read_csv(fp)
            mask = df["Model"].astype(str).str.contains("this study", case=False, na=False)
            if mask.any():
                au = pd.to_numeric(df.loc[mask, "AUROC"], errors="coerce").dropna()
                if len(au):
                    self.reference_auroc = float(au.iloc[-1])
        except Exception:
            pass

    def _load_bundle(self, prefix: str) -> bool:
        # prefix: "final" or "deploy"
        req = {
            "xgb": f"{prefix}_xgb_behavioural.joblib",
            "lr": f"{prefix}_lr_behavioural.joblib",
            "w": f"{prefix}_blend_weight.joblib",
            "prior": f"{prefix}_prior_correction.joblib",
            "thr": f"{prefix}_threshold.joblib",
        }
        paths = {k: os.path.join(MODEL_DIR, v) for k, v in req.items()}
        if not all(os.path.exists(p) for p in paths.values()):
            return False

        self.model_beh = joblib.load(paths["xgb"])
        self.model_lr = joblib.load(paths["lr"])
        self.blend_weight = float(joblib.load(paths["w"]))
        prior = joblib.load(paths["prior"])
        self.train_prior = float(prior["train_prior"])
        self.target_prior = float(prior["target_prior"])
        self.threshold = float(joblib.load(paths["thr"]))

        # Optional in deploy, expected in final
        dhs_fp = os.path.join(MODEL_DIR, f"{prefix}_dhs_comorbidity_params.joblib")
        if os.path.exists(dhs_fp):
            self.dhs_params = joblib.load(dhs_fp)

        self.models_loaded = True
        self.model_mode = prefix
        return True

    def _load_models(self):
        try:
            if self._load_bundle("final"):
                return
            if self._load_bundle("deploy"):
                return

            # Legacy fallback (older notebook output)
            self.model_beh = joblib.load(os.path.join(MODEL_DIR, "xgb_behavioural.joblib"))
            self.model_dem = joblib.load(os.path.join(MODEL_DIR, "xgb_demographic.joblib"))
            self.meta_model = joblib.load(os.path.join(MODEL_DIR, "meta_model.joblib"))
            self.threshold = float(joblib.load(os.path.join(MODEL_DIR, "threshold.joblib")))
            self.models_loaded = True
            self.model_mode = "legacy"

        except FileNotFoundError:
            self.models_loaded = False
            self.model_mode = "demo"

    @staticmethod
    def encode_responses(responses: dict) -> np.ndarray:
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
        return np.array([[
            age_months / 12.0,
            1 if sex == "Male" else 0,
            1 if jaundice else 0,
            1 if family_asd else 0,
        ]], dtype=float)

    @staticmethod
    def saerens_prior_correction(p: float, train_prior: float, target_prior: float) -> float:
        p = float(np.clip(p, 1e-6, 1 - 1e-6))
        num = p * (target_prior / train_prior)
        den = num + (1 - p) * ((1 - target_prior) / (1 - train_prior))
        return float(num / den)

    def _apply_population_comorbidity_adjustment(self, X_beh: np.ndarray) -> np.ndarray:
        # Matches notebook final-combined input adjustment (population-level)
        item_weights = self.dhs_params.get("item_weights", {})
        p_stunting = float(self.dhs_params.get("pop_stunting", 0.0))
        p_anaemia = float(self.dhs_params.get("pop_anaemia", 0.0))

        X_adj = X_beh.astype(float).copy()
        for i in range(X_adj.shape[1]):
            item = f"Q{i+1}"
            w = float(item_weights.get(item, 0.0))
            risk_factor = w * (0.5 * p_stunting + 0.3 * p_anaemia)
            adjustment = np.clip(risk_factor * 0.3, 0.0, w)
            X_adj[0, i] = X_adj[0, i] * (1.0 - adjustment)
        return X_adj

    @staticmethod
    def get_cultural_notes(responses: dict) -> dict:
        return {
            item_id: {"response": responses.get(item_id, "—"), "note": CULTURAL_NOTES[item_id]}
            for item_id in SPEECH_ITEMS
        }

    def runtime_summary(self) -> dict:
        return {
            "mode": self.model_mode,
            "threshold": float(self.threshold),
            "blend_weight": float(self.blend_weight) if self.model_mode in {"final", "deploy"} else None,
            "target_prior": self.target_prior,
            "reference_auroc": self.reference_auroc,
        }

    def predict(self, responses: dict, age_months: int, sex: str,
                stunted: bool = False, anaemic: bool = False,
                no_caregiver: bool = False, rural: bool = False,
                jaundice: bool = False, family_asd: bool = False,
                low_maternal_edu: bool = False, low_wealth: bool = False,
                inadequate_anc: bool = False, small_birth: bool = False,
                home_delivery: bool = False, short_interval: bool = False) -> dict:

        X_beh = self.encode_responses(responses)
        X_dem = self.encode_demographics(age_months, sex, jaundice, family_asd)

        if self.models_loaded and self.model_mode in {"final", "deploy"}:
            X_use = self._apply_population_comorbidity_adjustment(X_beh)
            prob_beh = float(self.model_beh.predict_proba(X_use)[0][1])
            prob_lr = float(self.model_lr.predict_proba(X_use)[0][1])

            prob_blend = float(self.blend_weight * prob_beh + (1.0 - self.blend_weight) * prob_lr)
            prob_cal = self.saerens_prior_correction(prob_blend, self.train_prior, self.target_prior)

            prob_dem = np.nan
            prob_fused = prob_blend
            demo_mode = False

            validation_note = (
                f"Using {self.model_mode} saved artifacts: behavioural ensemble + prior correction "
                f"(threshold={self.threshold:.3f})."
            )

        elif self.models_loaded and self.model_mode == "legacy":
            prob_beh = float(self.model_beh.predict_proba(X_beh)[0][1])
            prob_dem = float(self.model_dem.predict_proba(X_dem)[0][1])
            X_meta = np.array([[prob_beh, prob_dem]])
            prob_fused = float(self.meta_model.predict_proba(X_meta)[0][1])
            prob_cal = prob_fused
            demo_mode = False

            validation_note = (
                "Using legacy saved artifacts: behavioural + demographic + fusion meta-model."
            )

        else:
            prob_beh = float(np.clip(X_beh.sum() / 10.0, 0.0, 1.0))
            prob_dem = 0.30
            prob_fused = (prob_beh + prob_dem) / 2.0
            prob_cal = prob_fused
            demo_mode = True

            validation_note = "Models not found. Demo mode only."

        if self.reference_auroc is not None:
            validation_note += f" Reference AUROC from outputs: {self.reference_auroc:.3f}."

        return {
            "prob_behavioural": round(prob_beh, 4),
            "prob_demographic": None if np.isnan(prob_dem) else round(float(prob_dem), 4),
            "prob_fused": round(prob_fused, 4),
            "prob_calibrated": round(prob_cal, 4),
            "threshold": round(self.threshold, 4),
            "at_risk": bool(prob_cal >= self.threshold),
            "cultural_notes": self.get_cultural_notes(responses),
            "validation_note": validation_note,
            "demo_mode": demo_mode,
            "model_mode": self.model_mode,
        }

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