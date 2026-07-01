import pandas as pd
import numpy as np
import json

df = pd.read_csv("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

stats = {}

# Contract type churn
ct = df.groupby("Contract")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["contract_churn"] = {k: round(v, 2) for k, v in ct.items()}

# Payment method churn
pm = df.groupby("PaymentMethod")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["payment_churn"] = {k: round(v, 2) for k, v in pm.items()}

# Tenure buckets
df["tenure_bin"] = pd.cut(df["tenure"], bins=[0, 6, 12, 24, 48, 72, 100],
                          labels=["0-6", "6-12", "12-24", "24-48", "48-72", "72+"])
tb = df.groupby("tenure_bin", observed=True)["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["tenure_churn"] = {str(k): round(v, 2) for k, v in tb.items()}

# Internet service
isv = df.groupby("InternetService")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["internet_churn"] = {k: round(v, 2) for k, v in isv.items()}

# Senior citizen
sc = df.groupby("SeniorCitizen")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["senior_churn"] = {str(k): round(v, 2) for k, v in sc.items()}

# Partner / dependents
pdf = df.groupby(["Partner", "Dependents"])["Churn"].apply(lambda x: (x == "Yes").mean() * 100).round(2)
stats["partner_dep_churn"] = {str(k): round(v, 2) for k, v in pdf.items()}

# Monthly charges buckets
df["charge_bin"] = pd.qcut(df["MonthlyCharges"], q=4, labels=["Low", "Mid-Low", "Mid-High", "High"])
cb = df.groupby("charge_bin", observed=True)["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["charge_bucket_churn"] = {str(k): round(v, 2) for k, v in cb.items()}

# Avg tenure
stats["avg_tenure_churned"] = round(df[df["Churn"] == "Yes"]["tenure"].mean(), 1)
stats["avg_tenure_retained"] = round(df[df["Churn"] == "No"]["tenure"].mean(), 1)

# Avg monthly charges
stats["avg_mc_churned"] = round(df[df["Churn"] == "Yes"]["MonthlyCharges"].mean(), 1)
stats["avg_mc_retained"] = round(df[df["Churn"] == "No"]["MonthlyCharges"].mean(), 1)

# High-risk segment
high_risk = df[(df["tenure"] < 12) & (df["Contract"] == "Month-to-month") & (df["InternetService"] == "Fiber optic")]
stats["high_risk_count"] = len(high_risk)
stats["high_risk_churn_rate"] = round((high_risk["Churn"] == "Yes").mean() * 100, 1)
stats["high_risk_rev_loss"] = round(high_risk[high_risk["Churn"] == "Yes"]["MonthlyCharges"].sum(), 2)

# Paperless billing
pb = df.groupby("PaperlessBilling")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["paperless_churn"] = {k: round(v, 2) for k, v in pb.items()}

# Gender
gen = df.groupby("gender")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["gender_churn"] = {k: round(v, 2) for k, v in gen.items()}

# Multiple lines
ml = df.groupby("MultipleLines")["Churn"].apply(lambda x: (x == "Yes").mean() * 100)
stats["multiple_lines_churn"] = {k: round(v, 2) for k, v in ml.items()}

# Contract type counts
cc = df.groupby("Contract").size()
stats["contract_counts"] = {k: int(v) for k, v in cc.items()}

# Tenure counts
tc = df.groupby("tenure_bin", observed=True).size()
stats["tenure_counts"] = {str(k): int(v) for k, v in tc.items()}

# Churned revenue calcs
churned = df[df["Churn"] == "Yes"]
retained = df[df["Churn"] == "No"]
stats["churned_monthly_rev"] = round(churned["MonthlyCharges"].sum(), 2)
stats["retained_monthly_rev"] = round(retained["MonthlyCharges"].sum(), 2)
stats["total_monthly_rev"] = round(df["MonthlyCharges"].sum(), 2)
stats["pct_rev_at_risk"] = round(churned["MonthlyCharges"].sum() / df["MonthlyCharges"].sum() * 100, 2)

stats["churned_count"] = int(len(churned))
stats["retained_count"] = int(len(retained))

with open("outputs/eda_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

print(json.dumps(stats, indent=2))
