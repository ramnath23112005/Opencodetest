import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import json

PLOTS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "plots"
PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed_churn.csv"
MODELS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "models"
RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)


def load_data():
    df = pd.read_csv(PROCESSED_PATH)
    return df


def feature_importance(df):
    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X, y)

    importances = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False).head(15)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=importances, x="importance", y="feature", hue="feature", palette="viridis", legend=False)
    plt.title("Top 15 Feature Importances (Random Forest)")
    plt.xlabel("Importance")
    plt.tight_layout()
    path = PLOTS_DIR / "feature_importance.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Feature importance plot saved to {path}")

    return importances


def shap_analysis(df):
    try:
        import shap
        X = df.drop(columns=["Churn"])
        y = df["Churn"]

        model = joblib.load(MODELS_DIR / "XGBoost.pkl")

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X.sample(min(500, len(X)), random_state=42))

        plt.figure()
        shap.summary_plot(shap_values, X.sample(min(500, len(X)), random_state=42),
                          show=False, max_display=15)
        path = PLOTS_DIR / "shap_summary.png"
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"SHAP summary plot saved to {path}")
    except Exception as e:
        print(f"SHAP analysis skipped: {e}")


def customer_segmentation(df):
    seg_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    X_seg = df[seg_cols].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_seg)

    inertia = []
    K_range = range(2, 11)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertia.append(km.inertia_)

    plt.figure(figsize=(8, 4))
    plt.plot(K_range, inertia, "bo-")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method for Optimal k")
    plt.tight_layout()
    path = PLOTS_DIR / "kmeans_elbow.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Elbow plot saved to {path}")

    k = 4
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    df["Cluster"] = km.fit_predict(X_scaled)

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(df["tenure"], df["MonthlyCharges"],
                          c=df["Cluster"], cmap="viridis", alpha=0.6, s=30)
    plt.xlabel("Tenure (scaled)")
    plt.ylabel("Monthly Charges (scaled)")
    plt.title("Customer Segments (KMeans, k=4)")
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    path = PLOTS_DIR / "customer_segments.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Customer segments plot saved to {path}")

    cluster_stats = df.groupby("Cluster")[seg_cols + ["Churn"]].mean().round(3)
    print("\nCluster profiles:")
    print(cluster_stats)

    return df


def generate_report(raw_path: str = str(RAW_PATH)):
    raw = pd.read_csv(raw_path)
    raw["TotalCharges"] = pd.to_numeric(raw["TotalCharges"], errors="coerce")
    total = len(raw)
    churned = raw["Churn"].value_counts().get("Yes", 0)
    churn_rate = round(100 * churned / total, 2)
    monthly_loss = round(raw.loc[raw["Churn"] == "Yes", "MonthlyCharges"].sum(), 2)
    clv = round(raw["TotalCharges"].mean(), 2)
    avg_clv_churned = round(raw.loc[raw["Churn"] == "Yes", "TotalCharges"].mean(), 2)
    avg_clv_retained = round(raw.loc[raw["Churn"] == "No", "TotalCharges"].mean(), 2)

    kpis = {
        "Total Customers": int(total),
        "Churn Rate (%)": churn_rate,
        "Retention Rate (%)": round(100 - churn_rate, 2),
        "Monthly Revenue Loss ($)": monthly_loss,
        "Average CLV ($)": clv,
        "Avg CLV - Churned ($)": avg_clv_churned,
        "Avg CLV - Retained ($)": avg_clv_retained,
    }

    report_path = Path(__file__).resolve().parent.parent / "outputs" / "kpi_report.json"
    with open(report_path, "w") as f:
        json.dump(kpis, f, indent=2)
    print(f"\nKPI report saved to {report_path}")

    for k, v in kpis.items():
        print(f"  {k}: {v}")


def run():
    df = load_data()
    print("=" * 50)
    print("Feature Importance Analysis")
    print("=" * 50)
    imp = feature_importance(df)
    print(imp.to_string(index=False))

    print("\n" + "=" * 50)
    print("SHAP Analysis")
    print("=" * 50)
    shap_analysis(df)

    print("\n" + "=" * 50)
    print("Customer Segmentation")
    print("=" * 50)
    customer_segmentation(df)

    print("\n" + "=" * 50)
    print("KPI Report")
    print("=" * 50)
    generate_report()

    print("\nAll insight visualizations saved in outputs/plots/")


if __name__ == "__main__":
    run()
