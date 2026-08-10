# Model Selection Justification

*All numbers below are real, executed outputs from `notebooks/04_modeling.ipynb` — test-set performance, not training performance.*

## Baseline

A naive "predict no-churn for everyone" model scores **73.46% accuracy** and **0% recall**. It catches zero churners. This is the floor every candidate model must clear on the metrics that matter for the business — not the floor to compete against on accuracy.

## Full Comparison (test set)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic Regression (SMOTE)** ⭐ | 74.59% | 51.39% | **79.14%** | **62.32%** | 83.68% |
| Logistic Regression (class_weight) | 73.81% | 50.43% | 77.54% | 61.12% | 83.93% |
| XGBoost (scale_pos_weight) | 74.88% | 52.06% | 67.65% | 58.84% | 81.34% |
| KNN (SMOTE, k=15) | 68.91% | 45.25% | 81.55% | 58.21% | 80.86% |
| XGBoost (tuned, SMOTE) | 77.93% | 58.10% | 60.43% | 59.24% | 83.14% |
| XGBoost (SMOTE) | 77.93% | 58.54% | 57.75% | 58.14% | 82.12% |
| Random Forest (tuned, SMOTE) | 77.86% | 58.52% | 56.95% | 57.72% | 82.07% |
| Random Forest (SMOTE) | 77.71% | 58.29% | 56.42% | 57.34% | 82.02% |
| Random Forest (class_weight) | 78.28% | 61.72% | 47.86% | 53.92% | 82.00% |

## Final Model: **Logistic Regression, trained on SMOTE-balanced data**

**This is a genuine, non-obvious finding — not the "expected" answer.** On this particular dataset, the simplest, most interpretable model outperforms Random Forest and XGBoost on the two metrics this project decided (in Phase 0) matter most: **Recall** and **F1-score**. The tree-based ensembles post higher *accuracy* (up to 78.3%) but achieve it by being more conservative — they catch meaningfully fewer actual churners (as low as 47.9% recall for tuned Random Forest with class weighting) in exchange for fewer false alarms.

Given the Phase 0 decision that **a missed churner is more expensive than a wasted retention offer**, this is exactly the wrong tradeoff to make. Logistic Regression (SMOTE) catches **79.1% of customers who actually churn**, at the cost of a lower precision (51.4% — roughly 1 in 2 flagged customers is a false alarm). For a retention team whose intervention is a phone call or a discount offer (cheap relative to losing the customer entirely), this is the right side of the tradeoff.

**Why this happened, mechanically:** the engineered features (particularly `high_risk_flag`, `contract_ordinal`, and `tenure_group`) already encode a lot of the non-linear interaction structure that tree models would otherwise have to discover on their own. Once that interaction is handed to a linear model directly, Logistic Regression's SMOTE-balanced decision boundary generalizes slightly better on recall than the ensembles' more conservative, precision-leaning splits.

**Bonus:** Logistic Regression is also fully interpretable by design (coefficients + SHAP are exact and fast, see Phase 6), which is valuable for a tool retention agents and compliance teams will actually need to trust and audit — a real secondary advantage on top of the metric win, not the primary reason for the choice.

## What we optimized hyperparameters for

`GridSearchCV` for the two tuned candidates (Random Forest, XGBoost) scored on **F1**, not accuracy — F1 keeps recall high while still penalizing a model that would trivially maximize recall by flagging everyone as high-risk (which would be useless to the retention team in practice, see Phase 7).

## Artifacts produced

- `models/model.pkl` — final fitted Logistic Regression model
- `models/preprocessor.pkl` — fitted `ColumnTransformer` (scaler + encoder, fit on train only)
- `models/feature_names.pkl` — ordered feature list matching the preprocessor's output
- `models/final_model_comparison.csv` — full comparison table (source of the table above)
- Same three model artifacts are copied into `backend/app/model_artifacts/` for the live API to load directly.
