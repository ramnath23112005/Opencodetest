import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
PROCESSED_PATH = DATA_DIR / "processed_churn.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    missing = df["TotalCharges"].isna().sum()
    if missing:
        df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
        print(f"Filled {missing} missing TotalCharges with MonthlyCharges * tenure")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    le = LabelEncoder()
    df["Churn"] = le.fit_transform(df["Churn"])

    cat_cols = df.select_dtypes(include=["object", "str"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c != "customerID"]

    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    print(f"Encoded {len(cat_cols)} categorical columns -> {df.shape[1]} total features")
    return df


def scale_features(df: pd.DataFrame) -> pd.DataFrame:
    num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    print(f"Scaled numeric features: {num_cols}")
    return df


def remove_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    z_scores = np.abs((df[num_cols] - df[num_cols].mean()) / df[num_cols].std())
    mask = (z_scores < threshold).all(axis=1)
    removed = (~mask).sum()
    df = df[mask].reset_index(drop=True)
    print(f"Removed {removed} outlier rows (z-score > {threshold})")
    return df


def process():
    df = load_data()
    df = handle_missing(df)
    df = encode_categoricals(df)
    df = scale_features(df)
    df = remove_outliers(df)

    if "customerID" in df.columns:
        df.drop(columns=["customerID"], inplace=True)

    df.to_csv(PROCESSED_PATH, index=False)
    print(f"Processed data saved to {PROCESSED_PATH} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    process()
