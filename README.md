# Customer Churn Prediction

End-to-end machine learning pipeline for predicting customer churn using the Telco Customer Churn dataset.

## Pipeline

1. **Download** - Fetch dataset via KaggleHub
2. **Data Processing** - Clean, encode, and split data
3. **ML Pipeline** - Train Logistic Regression, Random Forest, and XGBoost models with hyperparameter tuning
4. **SQL Analysis** - Generate analytical SQL queries
5. **Insights & Visualizations** - Feature importance, SHAP explanations, KPI reports, customer segmentation (K-Means), and ROC comparisons

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python run_pipeline.py
```

## Outputs

- `outputs/models/` - Trained model pickles
- `outputs/plots/` - Confusion matrices, ROC curves, feature importance, SHAP summary, K-Means elbow & segments
- `outputs/model_results.json` - Model performance metrics
- `outputs/kpi_report.json` - Business KPIs
- `sql/churn_analysis.sql` - Analytical SQL queries

## Tech Stack

pandas, scikit-learn, XGBoost, SHAP, imbalanced-learn, matplotlib, seaborn
