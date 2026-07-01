import kagglehub
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

def download_dataset():
    path = kagglehub.dataset_download("blastchar/telco-customer-churn")
    for f in Path(path).iterdir():
        if f.suffix == ".csv":
            df = pd.read_csv(f)
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(RAW_PATH, index=False)
            print(f"Dataset saved to {RAW_PATH} ({len(df)} rows, {len(df.columns)} cols)")
            return df
    raise FileNotFoundError("No CSV found in downloaded dataset")

if __name__ == "__main__":
    download_dataset()
