"""
Model Evaluation - held-out performance of the placement-readiness model.

Reproduces exactly the train/test split used in train_model.py
(same synthetic generator, seed, 80/20 stratified split) and reports
standard classification metrics on the 20% the model never saw:
accuracy, precision, recall, F1, ROC-AUC, the confusion matrix, 5-fold
cross-validated accuracy, and global (impurity-based) feature importance.

Results are cached to ml_artifacts/model_metrics.json; train_model.py
refreshes that file every time the model is retrained.
"""
import importlib.util
import json
import os
from typing import Dict

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(BACKEND_DIR, "ml_artifacts")
MODEL_PATH = os.path.join(MODEL_DIR, "readiness_model.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")


def _load_training_module():
    spec = importlib.util.spec_from_file_location("train_model", os.path.join(BACKEND_DIR, "train_model.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(model, run_cv: bool = True) -> Dict:
    tm = _load_training_module()
    df = tm.generate_synthetic_dataset()
    X, y = df[tm.FEATURE_NAMES], df["placed"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()

    cv = None
    if run_cv:
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(clone(model), X, y, cv=folds, scoring="accuracy")
        cv = {"folds": 5, "mean": round(float(scores.mean()) * 100, 2), "std": round(float(scores.std()) * 100, 2)}

    # Baseline comparison on the identical split - justifies the model choice.
    baselines = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "K-Nearest Neighbours": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=15)),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, max_depth=2, random_state=42),
    }
    comparison = [{
        "model": "Random Forest (deployed)",
        "accuracy": round(accuracy_score(y_test, pred) * 100, 2),
        "f1": round(f1_score(y_test, pred) * 100, 2),
        "roc_auc": round(roc_auc_score(y_test, proba) * 100, 2),
        "explainable": "Exact TreeSHAP",
    }]
    for name, est in baselines.items():
        est.fit(X_train, y_train)
        p, pr = est.predict(X_test), est.predict_proba(X_test)[:, 1]
        comparison.append({
            "model": name,
            "accuracy": round(accuracy_score(y_test, p) * 100, 2),
            "f1": round(f1_score(y_test, p) * 100, 2),
            "roc_auc": round(roc_auc_score(y_test, pr) * 100, 2),
            "explainable": {"Logistic Regression": "Coefficients", "Decision Tree": "Exact TreeSHAP",
                            "Gradient Boosting": "Exact TreeSHAP"}.get(name, "Approximate only"),
        })

    importances = getattr(model, "feature_importances_", np.zeros(len(tm.FEATURE_NAMES)))
    ranked = sorted(zip(tm.FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)

    return {
        "algorithm": type(model).__name__,
        "hyperparameters": {k: v for k, v in model.get_params().items()
                            if k in ("n_estimators", "max_depth", "min_samples_leaf", "random_state")},
        "dataset": {
            "total": int(len(df)), "train": int(len(X_train)), "test": int(len(X_test)),
            "features": len(tm.FEATURE_NAMES), "positive_rate": round(float(y.mean()) * 100, 1),
            "source": "Synthetic, rule-based ground truth with Gaussian noise (see train_model.py)",
        },
        "metrics": {
            "accuracy": round(accuracy_score(y_test, pred) * 100, 2),
            "precision": round(precision_score(y_test, pred) * 100, 2),
            "recall": round(recall_score(y_test, pred) * 100, 2),
            "f1": round(f1_score(y_test, pred) * 100, 2),
            "roc_auc": round(roc_auc_score(y_test, proba) * 100, 2),
        },
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
                             "labels": ["Not placed", "Placed"]},
        "cross_validation": cv,
        "comparison": comparison,
        "feature_importance": [{"feature": f, "importance": round(float(v) * 100, 2)} for f, v in ranked],
    }


def get_metrics(refresh: bool = False) -> Dict:
    """Cached metrics; computed (and cached) on first request."""
    if not refresh and os.path.exists(METRICS_PATH):
        with open(METRICS_PATH) as f:
            return json.load(f)
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model artifact not found. Run `python train_model.py` first.")
    result = evaluate(joblib.load(MODEL_PATH))
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(METRICS_PATH, "w") as f:
        json.dump(result, f, indent=2)
    return result
