import os
import warnings
import numpy as np
import joblib
import pandas as pd

# Directory containing trained model artifacts and evaluation outputs
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

# Items 1-9: "Always"/"Usually" = typical (0), everything less frequent = atypical (1)
RESPONSE_OPTIONS = {
    "Always":    0,
    "Usually":   0,
    "Sometimes": 1,
    "Rarely":    1,
    "Never":     1,
}

# Q10 is reverse-keyed: staring at nothing OFTEN is the atypical answer
RESPONSE_OPTIONS_Q10 = {
    "Always":    1,
    "Usually":   1,
    "Sometimes": 1,
    "Rarely":    0,
    "Never":     0,
}

REVERSE_ITEMS = {"Q10"}
SPEECH_ITEMS = {"Q1", "Q8", "Q9"}

CULTURAL_NOTES = {
    "Q1": "Response to name may be influenced by language and communication patterns in Sesotho-speaking contexts.",
    "Q8": "Early speech development can vary across languages and cultures. This item may not transfer directly to Sesotho linguistic norms.",
    "Q9": "Gestures and social behaviours may differ across cultural settings. Cultural alignment analysis flagged this item.",
}


class AutismPredictor:
    """
    Loads the deploy_* bundle saved by the notebook (cell 38): a
    cross-validated XGBoost + Logistic Regression behavioural ensemble,
    blended with a CV-selected weight, Saerens prior-corrected to a ~1%
    deployment prevalence (Zeidan et al., 2022).

    The notebook also tried a DHS stunting/anaemia comorbidity adjustment
    (population-level and individual-level, cells 50-58) and a fairness
    reweighting experiment (cell 79), but concluded neither improved
    performance enough to ship -- see cells 56/64/81. Those experiments
    are documented in outputs/, not loaded here.
    """

    def __init__(self):
        self.model_beh = None
        self.model_lr = None

        self.threshold = 0.5
        self.blend_weight = 1.0
        self.train_prior = None
        self.target_prior = None

        self.models_loaded = False
        self.model_mode = "demo"  # deploy | demo
        self.reference_auroc = None
        self.lr_fallback_triggered = False  # visible flag if the sigmoid fallback ever fires

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

    def _load_models(self):
        req = {
            "xgb": "deploy_xgb_behavioural.joblib",
            "lr": "deploy_lr_behavioural.joblib",
            "w": "deploy_blend_weight.joblib",
            "prior": "deploy_prior_correction.joblib",
            "thr": "deploy_threshold.joblib",
        }
        paths = {k: os.path.join(MODEL_DIR, v) for k, v in req.items()}

        if not all(os.path.exists(p) for p in paths.values()):
            self.models_loaded = False
            self.model_mode = "demo"
            return

        self.model_beh = joblib.load(paths["xgb"])
        self.model_lr = joblib.load(paths["lr"])
        self.blend_weight = float(joblib.load(paths["w"]))
        prior = joblib.load(paths["prior"])
        self.train_prior = float(prior["train_prior"])
        self.target_prior = float(prior["target_prior"])
        self.threshold = float(joblib.load(paths["thr"]))

        self.models_loaded = True
        self.model_mode = "deploy"

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
    def saerens_prior_correction(p: float, train_prior: float, target_prior: float) -> float:
        p = float(np.clip(p, 1e-6, 1 - 1e-6))
        num = p * (target_prior / train_prior)
        den = num + (1 - p) * ((1 - target_prior) / (1 - train_prior))
        return float(num / den)

    def _safe_lr_predict_proba(self, X: np.ndarray) -> float:
        """
        Tries the real sklearn predict_proba() first. Only falls back to a
        hand-computed sigmoid if that call raises, and flags it visibly --
        the fallback is never silent. A triggered fallback means the
        environment that unpickled model_lr differs from the one that
        pickled it (re-pin requirements.txt to the training env and
        re-test; this is a symptom, not a fix).
        """
        try:
            return float(self.model_lr.predict_proba(X)[0][1])
        except Exception as e:
            self.lr_fallback_triggered = True
            warnings.warn(
                f"model_lr.predict_proba() failed ({type(e).__name__}: {e}); "
                f"falling back to manual sigmoid(coef_ . x + intercept_). "
                f"This is a version-skew symptom -- pin scikit-learn in "
                f"requirements.txt to match the training environment.",
                RuntimeWarning,
            )
            z = X @ self.model_lr.coef_.T + self.model_lr.intercept_
            return float(1.0 / (1.0 + np.exp(-z))[0][0])

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
            "blend_weight": float(self.blend_weight) if self.models_loaded else None,
            "target_prior": self.target_prior,
            "reference_auroc": self.reference_auroc,
            "lr_fallback_triggered": self.lr_fallback_triggered,
        }

    def predict(self, responses: dict, age_months: int, sex: str,
                jaundice: bool = False, family_asd: bool = False) -> dict:
        # age_months/sex/jaundice/family_asd are collected for the parent's
        # own record only -- the deployed model scores Q-CHAT-10 answers
        # alone, so they're accepted here but not used.
        X_beh = self.encode_responses(responses)

        if self.models_loaded:
            prob_beh = float(self.model_beh.predict_proba(X_beh)[0][1])
            prob_lr = self._safe_lr_predict_proba(X_beh)

            prob_blend = float(self.blend_weight * prob_beh + (1.0 - self.blend_weight) * prob_lr)
            prob_cal = self.saerens_prior_correction(prob_blend, self.train_prior, self.target_prior)
            prob_fused = prob_blend

            validation_note = (
                f"Behavioural ensemble (XGBoost weight={self.blend_weight:.2f}) + "
                f"prior correction to ~{self.target_prior:.1%} deployment prevalence "
                f"(threshold={self.threshold:.4f}). Score is based on Q-CHAT-10 "
                f"responses only. A DHS stunting/anaemia comorbidity adjustment was "
                f"tested during development at both the population and individual "
                f"level but did not improve performance enough to justify shipping "
                f"it, so it is not part of this model."
            )

            if self.lr_fallback_triggered:
                validation_note += (
                    " [Note: the logistic-regression component used a manual "
                    "fallback computation this run due to a model-loading "
                    "issue -- see server logs.]"
                )

        else:
            prob_beh = float(np.clip(X_beh.sum() / 10.0, 0.0, 1.0))
            prob_fused = prob_beh
            prob_cal = prob_fused
            validation_note = "Models not found. Demo mode only -- score is illustrative, not calibrated."

        if self.reference_auroc is not None:
            validation_note += f" Reference AUROC from outputs: {self.reference_auroc:.3f}."

        return {
            "prob_behavioural": round(prob_beh, 4),
            "prob_demographic": None,
            "prob_fused": round(prob_fused, 4),
            "prob_calibrated": round(prob_cal, 4),
            "threshold": round(self.threshold, 4),
            "at_risk": bool(prob_cal >= self.threshold),
            "cultural_notes": self.get_cultural_notes(responses),
            "validation_note": validation_note,
            "demo_mode": self.model_mode == "demo",
            "model_mode": self.model_mode,
        }


_instance = None


def get_predictor() -> "AutismPredictor":
    global _instance
    if _instance is None:
        _instance = AutismPredictor()
    return _instance


if __name__ == "__main__":
    result = AutismPredictor().predict(
        responses={
            "Q1": "Rarely", "Q2": "Sometimes", "Q3": "Never", "Q4": "Never",
            "Q5": "Sometimes", "Q6": "Sometimes", "Q7": "Rarely", "Q8": "Rarely",
            "Q9": "Sometimes", "Q10": "Always",
        },
        age_months=24,
        sex="Male",
    )
    print(result)