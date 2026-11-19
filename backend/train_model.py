"""
Trains the placement-readiness RandomForest classifier used by
app/services/ml_model.py.

Run once before starting the API:
    python train_model.py

Generates a synthetic dataset with a transparent, rule-based ground truth
(so the demo model reflects intuitive placement-readiness logic), trains a
RandomForestClassifier, and saves it to ml_artifacts/readiness_model.joblib.

Replace `generate_synthetic_dataset()` with a loader for real historical
placement records to retrain on actual institutional data.
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

FEATURE_NAMES = [
    "cgpa", "attendance", "aptitude_score", "coding_score", "communication_score",
    "internship_months", "num_technical_skills", "num_certifications", "num_projects",
    "ats_score", "resume_quality_score", "interview_technical_score",
    "interview_communication_score", "interview_confidence_score",
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ml_artifacts")


def generate_synthetic_dataset(n=4000, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    data = {
        "cgpa": rng.uniform(5.0, 10.0, n),
        "attendance": rng.uniform(50, 100, n),
        "aptitude_score": rng.uniform(30, 100, n),
        "coding_score": rng.uniform(0, 100, n),
        "communication_score": rng.uniform(20, 100, n),
        "internship_months": rng.integers(0, 12, n),
        "num_technical_skills": rng.integers(0, 15, n),
        "num_certifications": rng.integers(0, 6, n),
        "num_projects": rng.integers(0, 8, n),
        "ats_score": rng.uniform(20, 100, n),
        "resume_quality_score": rng.uniform(20, 100, n),
        "interview_technical_score": rng.uniform(0, 100, n),
        "interview_communication_score": rng.uniform(0, 100, n),
        "interview_confidence_score": rng.uniform(0, 100, n),
    }
    df = pd.DataFrame(data)

    # Transparent weighted-sum "ground truth" so SHAP explanations line up
    # with intuitive placement-readiness factors, plus noise for realism.
    weighted = (
        0.14 * (df.cgpa / 10 * 100) +
        0.05 * df.attendance +
        0.10 * df.aptitude_score +
        0.14 * df.coding_score +
        0.10 * df.communication_score +
        0.06 * (df.internship_months / 12 * 100) +
        0.07 * (df.num_technical_skills / 15 * 100) +
        0.04 * (df.num_certifications / 6 * 100) +
        0.06 * (df.num_projects / 8 * 100) +
        0.08 * df.ats_score +
        0.04 * df.resume_quality_score +
        0.06 * df.interview_technical_score +
        0.03 * df.interview_communication_score +
        0.03 * df.interview_confidence_score
    )
    noise = rng.normal(0, 6, n)
    composite = weighted + noise
    threshold = np.percentile(composite, 45)  # ~55% placed, realistic class balance
    df["placed"] = (composite >= threshold).astype(int)
    return df


def train():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = generate_synthetic_dataset()

    X = df[FEATURE_NAMES]
    y = df["placed"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=5, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Validation accuracy: {acc:.4f}")
    print(classification_report(y_test, preds, target_names=["Not Placed", "Placed"]))

    joblib.dump(model, os.path.join(OUTPUT_DIR, "readiness_model.joblib"))
    print(f"Model saved to {os.path.join(OUTPUT_DIR, 'readiness_model.joblib')}")

    # Refresh the cached evaluation report shown on the Prediction page.
    from app.services.model_evaluation import get_metrics
    report = get_metrics(refresh=True)
    m = report["metrics"]
    print(f"Held-out metrics: accuracy {m['accuracy']}%, precision {m['precision']}%, "
          f"recall {m['recall']}%, F1 {m['f1']}%, ROC-AUC {m['roc_auc']}%")


if __name__ == "__main__":
    train()
