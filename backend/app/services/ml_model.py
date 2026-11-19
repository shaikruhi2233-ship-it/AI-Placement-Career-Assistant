"""
Module 8 & 9 - Placement Readiness Prediction + Explainable AI.

Loads the pre-trained RandomForest classifier (see train_model.py) and
produces a placement-readiness prediction alongside a SHAP-based
explanation identifying which factors pushed the score up or down.
"""
import os
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
import shap

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml_artifacts")
MODEL_PATH = os.path.join(MODEL_DIR, "readiness_model.joblib")

FEATURE_NAMES = [
    "cgpa", "attendance", "aptitude_score", "coding_score", "communication_score",
    "internship_months", "num_technical_skills", "num_certifications", "num_projects",
    "ats_score", "resume_quality_score", "interview_technical_score",
    "interview_communication_score", "interview_confidence_score",
]

# Human-readable labels (underscores removed) for the explainability table.
FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    "cgpa": "CGPA",
    "attendance": "Attendance",
    "aptitude_score": "Aptitude Score",
    "coding_score": "Coding Score",
    "communication_score": "Communication Score",
    "internship_months": "Internship Months",
    "num_technical_skills": "Technical Skills Count",
    "num_certifications": "Certifications Count",
    "num_projects": "Projects Count",
    "ats_score": "ATS Score",
    "resume_quality_score": "Resume Quality Score",
    "interview_technical_score": "Interview Technical Score",
    "interview_communication_score": "Interview Communication Score",
    "interview_confidence_score": "Interview Confidence Score",
}

# Reasonable ceiling per feature, used only to normalise its raw value onto
# a 0-100 scale before banding it into a High/Medium/Average/Below Average/
# Low rating — feature scales differ wildly (CGPA is 0-10, counts are
# small integers, scores are 0-100) so a rating needs this normalisation.
FEATURE_MAX_VALUES: Dict[str, float] = {
    "cgpa": 10.0, "attendance": 100.0, "aptitude_score": 100.0, "coding_score": 100.0,
    "communication_score": 100.0, "internship_months": 12.0, "num_technical_skills": 15.0,
    "num_certifications": 8.0, "num_projects": 8.0, "ats_score": 100.0,
    "resume_quality_score": 100.0, "interview_technical_score": 100.0,
    "interview_communication_score": 100.0, "interview_confidence_score": 100.0,
}


def _display_name(feature: str) -> str:
    return FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " ").title())


def _normalize_pct(feature: str, value: float) -> float:
    max_value = FEATURE_MAX_VALUES.get(feature, 100.0) or 1.0
    return min(max(value, 0.0) / max_value * 100, 100)


def _band(pct: float) -> str:
    if pct >= 80:
        return "High"
    if pct >= 65:
        return "Medium"
    if pct >= 50:
        return "Average"
    if pct >= 35:
        return "Below Average"
    return "Low"


def _rating(feature: str, value: float) -> str:
    return _band(_normalize_pct(feature, value))


# Groups of raw features rolled up into one readable performance category
# each, for the "Performance Status" summary (separate from the per-feature
# breakdown table).
CATEGORY_GROUPS: Dict[str, List[str]] = {
    "Academic Performance": ["cgpa", "attendance", "aptitude_score"],
    "Technical & Project Performance": [
        "coding_score", "num_technical_skills", "num_certifications", "num_projects", "internship_months",
    ],
    "Resume Performance": ["ats_score", "resume_quality_score"],
    "Interview Performance": [
        "interview_technical_score", "interview_communication_score", "interview_confidence_score",
        "communication_score",
    ],
}


def _performance_status(features: Dict[str, float]) -> List[dict]:
    status = []
    for category, feats in CATEGORY_GROUPS.items():
        pcts = [_normalize_pct(f, features.get(f, 0.0)) for f in feats]
        avg_pct = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
        status.append({"category": category, "score_percent": avg_pct, "rating": _band(avg_pct)})
    return status


_model = None
_explainer = None


def _load():
    global _model, _explainer
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model artifact not found. Run `python train_model.py` from the backend/ "
                "directory once before starting the API."
            )
        _model = joblib.load(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)
    return _model, _explainer


def build_feature_vector(features: Dict[str, float]) -> pd.DataFrame:
    row = {name: features.get(name, 0.0) for name in FEATURE_NAMES}
    return pd.DataFrame([row], columns=FEATURE_NAMES)


def predict_readiness(features: Dict[str, float]) -> dict:
    model, explainer = _load()
    X = build_feature_vector(features)

    proba = model.predict_proba(X)[0]
    placement_probability = round(float(proba[1]) * 100, 2)
    readiness_score = placement_probability  # single composite score, 0-100

    if readiness_score >= 75:
        label = "Ready"
    elif readiness_score >= 50:
        label = "Moderate"
    else:
        label = "Needs Work"

    shap_values = explainer.shap_values(X)
    # shap_values shape for binary RF: [class0_array, class1_array] or (n,features,2)
    if isinstance(shap_values, list):
        contrib = shap_values[1][0]
    else:
        contrib = shap_values[0][:, 1] if shap_values.ndim == 3 else shap_values[0]

    contributions = list(zip(FEATURE_NAMES, contrib))
    contributions.sort(key=lambda x: x[1], reverse=True)

    top_positive = [f"{_display_name(name)} (+{val:.3f})" for name, val in contributions if val > 0][:5]
    top_negative = [f"{_display_name(name)} ({val:.3f})" for name, val in contributions if val < 0][:5]

    feature_importance = {name: round(float(val), 4) for name, val in contributions}

    # Explainable breakdown for the UI: clean display name, the student's
    # actual value for this feature, that value normalised onto a plain
    # 0-100% scale (score_percent), and a High/Medium/Average/Below
    # Average/Low rating of it.
    feature_breakdown = [
        {
            "feature": name,
            "display_name": _display_name(name),
            "value": round(float(features.get(name, 0.0)), 2),
            "score_percent": round(_normalize_pct(name, float(features.get(name, 0.0))), 2),
            "rating": _rating(name, float(features.get(name, 0.0))),
        }
        for name, val in contributions
    ]

    confidence_score = round(float(max(proba)) * 100, 2)

    return {
        "readiness_score": readiness_score,
        "placement_probability": placement_probability,
        "confidence_score": confidence_score,
        "readiness_label": label,
        "feature_importance": feature_importance,
        "feature_breakdown": feature_breakdown,
        "performance_status": _performance_status(features),
        "top_positive_factors": top_positive,
        "top_negative_factors": top_negative,
    }
