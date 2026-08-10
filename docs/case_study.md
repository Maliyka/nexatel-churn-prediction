# Case Study: Predicting Customer Churn Before It Happens

*NexaTel Customer Churn Prediction & Retention Intelligence System — data science capstone project*

## Problem

NexaTel, a regional telecom provider, was losing over a quarter of its customers (26.5%) every cycle, representing roughly $1.67M in annualized recurring revenue. The company had no way to know a customer was at risk until after they'd already cancelled, so retention offers went out reactively and inconsistently — wasting budget on loyal customers while genuinely at-risk ones slipped away unnoticed.

## Approach

I treated this as a full, end-to-end data science problem rather than a single notebook exercise:

- **Database first:** normalized the raw customer extract into a proper 3NF PostgreSQL schema (customers, accounts, services, churn outcomes) and answered 15 core business questions directly in SQL before writing a line of modeling code.
- **Evidence-driven feature engineering:** every engineered feature (a combined "new + month-to-month + no tech support" risk flag, a manual-payment risk flag, tenure buckets) was built directly from a pattern found in the SQL/EDA layer, not guessed at.
- **Metric discipline:** decided upfront that a missed churner costs the business far more than a wasted retention offer, and optimized every downstream step — model selection, hyperparameter tuning, risk thresholds — for Recall and F1, not Accuracy.
- **Explainability, not just a score:** every prediction ships with the top 3 SHAP-derived reasons behind it, so a retention agent gets a plain-language justification, not a black-box number.
- **Shipped, not just modeled:** built and deployed a full-stack web app (FastAPI + React) a non-technical retention agent can actually use — not just a notebook with a good AUC score.

## Key Insight

The most useful finding wasn't the model itself — it was a single SQL query. Customers with **under 6 months of tenure, a month-to-month contract, and no tech support churn 66.5% of the time** — more than double the company-wide rate, and a segment large enough (908 customers) and cheap enough to identify (three fields, known at signup) to be worth a standing retention campaign on its own, independent of the model.

The model added a second, less obvious insight: the simplest model in the comparison — Logistic Regression — beat Random Forest and XGBoost on Recall and F1, because the engineered features had already done the work of encoding the non-linear interactions those ensembles would otherwise need to discover themselves. Higher accuracy isn't always the better model for the business question actually being asked.

## Result

- Final model catches **79.1% of customers who actually churn** (vs. 0% for a naive baseline), at 83.7% ROC-AUC.
- Every prediction comes with the top 3 factors driving it and a concrete suggested retention action, generated live.
- Shipped as a working app: a retention agent fills out a short form and gets a risk score, a plain-language explanation, and a next step in under 5 seconds.

## Business Impact

If this system helps the retention team successfully intervene on even 10% of the customers it correctly flags as high-risk, that's roughly **$167,000/year** in protected recurring revenue — from a model that costs nothing to run beyond normal cloud hosting, and a tool that requires no data science background to use.

---
*Full technical writeup, code, and live demo: [GitHub repository link] · [Live app link]*
