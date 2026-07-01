import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))


def main():
    print("=" * 60)
    print("CUSTOMER CHURN PREDICTION PIPELINE")
    print("=" * 60)

    print("\n[1/5] Downloading dataset...")
    from download_data import download_dataset
    download_dataset()

    print("\n[2/5] Processing data...")
    from data_processing import process
    process()

    print("\n[3/5] Running ML pipeline...")
    from ml_pipeline import run_pipeline
    results, models = run_pipeline()

    print("\n[4/5] Generating SQL analysis...")
    from sql_analysis import SQL_QUERIES
    sql_path = Path(__file__).resolve().parent / "sql" / "churn_analysis.sql"
    with open(sql_path, "w") as f:
        f.write(SQL_QUERIES)
    print(f"SQL queries at {sql_path}")

    print("\n[5/5] Generating insights & visualizations...")
    from insights import run
    run()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Processed data: data/processed_churn.csv")
    print(f"  - Trained models: outputs/models/")
    print(f"  - Plots:         outputs/plots/")
    print(f"  - Results:       outputs/model_results.json")
    print(f"  - KPI report:    outputs/kpi_report.json")
    print(f"  - SQL queries:   sql/churn_analysis.sql")


if __name__ == "__main__":
    main()
