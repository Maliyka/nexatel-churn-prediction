# Resume Bullet Points

Pick 2–3 depending on the role you're applying for. All numbers are real, sourced from `docs/model_selection_justification.md` and `docs/sql_findings_summary.md` — defend any of them directly if asked in an interview.

## General / Data Science roles

- Built and deployed an end-to-end churn prediction system (PostgreSQL → FastAPI → React) that identifies at-risk telecom customers with **79.1% recall**, achieving 83.7% ROC-AUC on a held-out test set, projected to help protect over **$1.6M in annualized recurring revenue**.
- Designed a normalized PostgreSQL schema and wrote 15 business-facing SQL queries that surfaced a single highest-risk customer segment (66.5% churn rate) directly used to drive feature engineering and retention targeting.
- Trained and compared 8 model/class-imbalance strategy combinations (Logistic Regression, Random Forest, XGBoost, KNN × SMOTE / class-weighting), selected and defended a final model based on business-aligned metrics (Recall/F1) rather than raw accuracy.

## Emphasizing full-stack / product delivery

- Shipped a full-stack churn-risk web application (FastAPI backend, React frontend, deployed on Render + Vercel) that turns a machine learning model into a tool non-technical retention agents use directly — no notebook or code required.
- Built a shared feature-engineering pipeline used identically at training and inference time, eliminating train/serve skew between the notebook-based model training and the live prediction API.

## Emphasizing explainability / stakeholder communication

- Integrated SHAP-based explainability into a live prediction API, surfacing the top 3 human-readable factors behind every churn-risk score in real time, turning a black-box model into an actionable tool for a non-technical audience.
- Translated a vague executive-level business complaint ("churn is too high") into a defensible, quantified data science problem — including a specific revenue-at-risk figure, explicit metric tradeoff decision, and 10 concrete business questions answered directly in SQL.
