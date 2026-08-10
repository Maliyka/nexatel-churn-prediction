"""
ml/explain.py
==============
SHAP-based explainability, shared between the notebook (05_explainability.ipynb)
and the live backend (/predict endpoint). The final model (Logistic Regression)
is a linear model, so we use shap.LinearExplainer, which is exact and fast
enough to run per-request in the API with no caching needed.
"""

import numpy as np
import shap


# Human-readable labels for the raw feature names produced by the
# ColumnTransformer, so explanations read naturally in the app instead of
# showing raw column names like 'nom__internet_service_Fiber optic'.
FRIENDLY_NAMES = {
    "tenure": "Account tenure",
    "monthly_charges": "Monthly bill amount",
    "total_charges": "Lifetime total charges",
    "total_services": "Number of add-on services",
    "avg_monthly_spend_ratio": "Average monthly spend",
    "contract_ordinal": "Contract commitment length",
    "senior_citizen": "Senior citizen status",
    "partner": "Has a partner",
    "dependents": "Has dependents",
    "paperless_billing": "Paperless billing",
    "high_risk_flag": "New + month-to-month + no tech support",
    "payment_risk_flag": "Manual payment method",
}


def _friendly(feature_name: str) -> str:
    base = feature_name.split("_", 1)
    if feature_name in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[feature_name]
    # One-hot columns look like "internet_service_Fiber optic"
    for key, label in FRIENDLY_NAMES.items():
        if feature_name.startswith(key):
            return label
    return feature_name.replace("_", " ").title()


def build_explainer(model, background_data):
    """background_data: a representative (already-preprocessed) sample of
    training data, used as the SHAP baseline distribution."""
    return shap.LinearExplainer(model, background_data)


def top_reasons_for_customer(explainer, X_row_processed, feature_names, top_n=3):
    """Return the top N features pushing this single customer's prediction
    toward or away from churn, as a list of dicts ready for JSON/API output.

    X_row_processed: a (1, n_features) preprocessed feature array.
    """
    shap_values = explainer.shap_values(X_row_processed)
    if isinstance(shap_values, list):  # some SHAP versions return a list per class
        shap_values = shap_values[0]
    shap_values = np.array(shap_values).reshape(-1)

    order = np.argsort(-np.abs(shap_values))[:top_n]

    reasons = []
    for idx in order:
        impact = float(shap_values[idx])
        reasons.append({
            "feature": _friendly(feature_names[idx]),
            "impact": round(impact, 4),
            "direction": "increases risk" if impact > 0 else "decreases risk",
        })
    return reasons
