"""
app/predict.py
================
Loads the trained model + preprocessor once at startup, and exposes a single
`predict_customer()` function used by the /predict route. This is the exact
same feature-engineering code path used in training (ml/feature_engineering.py),
imported from the self-contained copy in app/ml/ — see README for why the
package is duplicated rather than imported from the repo root.
"""

import os
import joblib
import numpy as np
import pandas as pd

from app.ml.feature_engineering import engineer_features, ALL_MODEL_COLUMNS
from app.ml.explain import build_explainer, top_reasons_for_customer

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "model_artifacts")

_model = joblib.load(os.path.join(ARTIFACTS_DIR, "model.pkl"))
_preprocessor = joblib.load(os.path.join(ARTIFACTS_DIR, "preprocessor.pkl"))
_feature_names = joblib.load(os.path.join(ARTIFACTS_DIR, "feature_names.pkl"))
_background = pd.read_csv(os.path.join(ARTIFACTS_DIR, "background_sample.csv"))
_explainer = build_explainer(_model, _background)

_model_name_path = os.path.join(ARTIFACTS_DIR, "FINAL_MODEL_NAME.txt")
_model_name = open(_model_name_path).read().strip() if os.path.exists(_model_name_path) else "Logistic Regression (SMOTE)"


def _risk_level(probability: float) -> str:
    """Fixed business thresholds, chosen so 'High' roughly matches the
    highest-risk deciles found in EDA/SQL (e.g. the tenure<6 + no tech
    support segment churns at 66.5%) rather than an arbitrary 50/50 split."""
    if probability >= 0.60:
        return "High"
    elif probability >= 0.30:
        return "Medium"
    return "Low"


def _suggested_action(customer: dict, risk_level: str, reasons: list) -> str:
    if risk_level == "Low":
        return "No action needed — customer is not currently at elevated risk."

    reason_features = {r["feature"] for r in reasons}

    if customer.get("contract") == "Month-to-month" and risk_level == "High":
        return "Offer a discounted 1-year or 2-year contract upgrade — contract length is the single strongest retention lever for this customer."
    if "Manual payment method" in reason_features:
        return "Offer an incentive to switch to autopay (bank transfer or credit card) — manual payers churn ~3x more often."
    if "Number of add-on services" in reason_features or customer.get("tech_support") == "No":
        return "Offer a free trial of Tech Support / online security add-ons — customers with more bundled services churn far less."
    if risk_level == "High":
        return "Escalate to a retention agent for a proactive outreach call before the next billing cycle."
    return "Monitor and consider a small loyalty incentive at next renewal."


def predict_customer(customer_input: dict) -> dict:
    """customer_input: dict matching schemas.CustomerInput field names."""
    row = pd.DataFrame([customer_input])

    # total_charges may be None (e.g. brand-new customer) -- engineer_features
    # / clean_raw already handles NaN -> monthly_charges fallback.
    if row.loc[0, "total_charges"] is None:
        row.loc[0, "total_charges"] = np.nan

    engineered = engineer_features(row)
    X = engineered[ALL_MODEL_COLUMNS]

    X_processed = _preprocessor.transform(X)
    X_processed = pd.DataFrame(X_processed, columns=_feature_names)
    probability = float(_model.predict_proba(X_processed)[0, 1])
    risk_level = _risk_level(probability)

    reasons = top_reasons_for_customer(_explainer, X_processed.values, _feature_names, top_n=3)
    action = _suggested_action(customer_input, risk_level, reasons)

    return {
        "churn_probability": round(probability, 4),
        "risk_level": risk_level,
        "top_reasons": reasons,
        "suggested_action": action,
        "model_name": _model_name,
    }
