import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score, roc_curve, confusion_matrix,
    classification_report, accuracy_score, precision_score,
    recall_score, f1_score
)
import joblib

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
MODELS_DIR = OUTPUT_DIR / "models"
PLOTS_DIR = OUTPUT_DIR / "plots"
PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed_churn.csv"

MODELS = {
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=6,
                              random_state=42, eval_metric="logloss"),
}


def load_processed() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_PATH)
    print(f"Loaded processed data: {len(df)} rows, {len(df.columns)} cols")
    return df


def split_data(df: pd.DataFrame, target: str = "Churn"):
    X = df.drop(columns=[target])
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test


def cross_validate(model, X_train, y_train, cv: int = 5):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="roc_auc")
    print(f"  CV ROC-AUC: {scores.mean():.4f} (+/- {scores.std():.4f})")
    return scores


def evaluate_model(name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "Accuracy": round(accuracy_score(y_test, y_pred), 4),
        "Precision": round(precision_score(y_test, y_pred), 4),
        "Recall": round(recall_score(y_test, y_pred), 4),
        "F1": round(f1_score(y_test, y_pred), 4),
        "ROC-AUC": round(roc_auc_score(y_test, y_proba), 4) if y_proba is not None else None,
    }

    print(f"\n{'='*50}")
    print(f"{name}")
    print(f"{'='*50}")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print(f"\n{classification_report(y_test, y_pred)}")

    return metrics, y_pred, y_proba


def plot_confusion_matrix(name, y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(f"{name} - Confusion Matrix")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    path = PLOTS_DIR / f"{name}_confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Confusion matrix saved to {path}")


def plot_roc_curves(models_dict, X_test, y_test):
    plt.figure(figsize=(8, 6))
    for name, model in models_dict.items():
        y_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.4f})")

    plt.plot([0, 1], [0, 1], "k--", label="Random")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves")
    plt.legend(loc="lower right")
    path = PLOTS_DIR / "roc_curves_comparison.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"ROC curves saved to {path}")


def run_pipeline():
    df = load_processed()
    X_train, X_test, y_train, y_test = split_data(df)

    results = {}
    trained_models = {}

    for name, model in MODELS.items():
        print(f"\n--- {name} ---")
        cv_scores = cross_validate(model, X_train, y_train)
        model.fit(X_train, y_train)
        metrics, y_pred, y_proba = evaluate_model(name, model, X_test, y_test)
        plot_confusion_matrix(name, y_test, y_pred)
        metrics["CV_ROC_AUC_mean"] = round(cv_scores.mean(), 4)
        metrics["CV_ROC_AUC_std"] = round(cv_scores.std(), 4)
        results[name] = metrics
        trained_models[name] = model

        model_path = MODELS_DIR / f"{name}.pkl"
        joblib.dump(model, model_path)
        print(f"  Model saved to {model_path}")

    plot_roc_curves(trained_models, X_test, y_test)

    results_path = OUTPUT_DIR / "model_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    best = max(results, key=lambda k: results[k]["ROC-AUC"])
    print(f"\nBest model: {best} (ROC-AUC={results[best]['ROC-AUC']})")

    return results, trained_models


if __name__ == "__main__":
    run_pipeline()
