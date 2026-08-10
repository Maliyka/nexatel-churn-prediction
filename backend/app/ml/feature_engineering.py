"""
ml/feature_engineering.py
==========================
Single source of truth for feature engineering. Imported by:
  - notebooks/02_feature_engineering.ipynb   (exploration + justification)
  - notebooks/03_preprocessing.ipynb          (build train/test sets)
  - backend/app/predict.py                    (live inference)

Keeping this logic in one shared module — instead of copy-pasting it into
the notebook AND the API — is what prevents "training/serving skew": the
single most common way real churn-prediction systems silently break in
production.
"""

import pandas as pd
import numpy as np

# ----------------------------------------------------------------------------
# Feature justification table — used in docs and printed in the notebook.
# ----------------------------------------------------------------------------
FEATURE_JUSTIFICATIONS = {
    "tenure_group": (
        "Bucketing raw tenure (0-12, 13-24, 25-48, 49+ months) lets tree models "
        "split on a coarser, more stable signal and lets the linear model treat "
        "'new customer' as a discrete risk category. EDA (Phase 2) showed churn "
        "risk is heavily concentrated in the first 12 months, then drops off — a "
        "non-linear relationship a single continuous tenure coefficient can't fully capture."
    ),
    "total_services": (
        "Counts how many of the 6 add-on services (security, backup, device "
        "protection, tech support, streaming TV, streaming movies) a customer has. "
        "SQL/EDA findings show churn falls steadily as this count rises (from ~46% "
        "at 1 service down to ~5% at 6) — this single number compresses six "
        "categorical columns into one strong, monotonic-ish signal."
    ),
    "avg_monthly_spend_ratio": (
        "TotalCharges / tenure, i.e. a customer's true average spend per month "
        "over their whole relationship (vs. their *current* MonthlyCharges, which "
        "may have changed). Large gaps between this and current MonthlyCharges can "
        "indicate a recent plan change, which is itself often a precursor to churn. "
        "For tenure = 0 customers, this is set equal to MonthlyCharges (their only "
        "observed month) rather than left undefined."
    ),
    "high_risk_flag": (
        "A binary flag for the exact segment SQL analysis found to be sharpest: "
        "tenure < 6 months AND contract = Month-to-month AND no tech support. "
        "That segment churns at 66.5% vs. 26.5% overall. Giving the model this "
        "combination directly (not just the three underlying columns) makes it "
        "easier for linear models to pick up an interaction that in reality is "
        "highly non-additive."
    ),
    "payment_risk_flag": (
        "A binary flag for manual payment methods (Electronic check or Mailed "
        "check) vs. automatic payment (Bank transfer or Credit card, both "
        "automatic). SQL findings show manual/electronic-check payers churn at "
        "roughly 3x the rate of autopay customers — likely because manual payment "
        "creates a natural monthly 'should I keep this?' decision point autopay "
        "customers never face."
    ),
    "contract_ordinal": (
        "Contract has a genuine order (Month-to-month < One year < Two year) in "
        "terms of commitment level, so it is ordinal-encoded (0/1/2) rather than "
        "one-hot encoded for models where that ordering is meaningful signal on "
        "its own (and one-hot encoded in parallel for models that don't assume order)."
    ),
}


def clean_raw(df: pd.DataFrame) -> pd.DataFrame:
    """Fix the data-quality issues identified in EDA. Idempotent and safe to
    call on a single-row DataFrame (live prediction) or the full dataset."""
    df = df.copy()

    # TotalCharges: blank for tenure=0 customers -> treat as their one month
    # of spend, i.e. equal to MonthlyCharges, not zero and not dropped.
    if "total_charges" in df.columns:
        df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    if "total_charges" in df.columns and "monthly_charges" in df.columns:
        mask = df["total_charges"].isna()
        df.loc[mask, "total_charges"] = df.loc[mask, "monthly_charges"]

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add all engineered features to a cleaned dataframe. Expects the
    snake_case column names used by the database schema (customer_id,
    tenure, monthly_charges, total_charges, contract, tech_support, ...).
    """
    df = clean_raw(df)

    # --- tenure_group -------------------------------------------------------
    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[-1, 12, 24, 48, 10_000],
        labels=["0-12", "13-24", "25-48", "49+"],
    ).astype(str)

    # --- total_services -------------------------------------------------------
    addon_cols = [
        "online_security", "online_backup", "device_protection",
        "tech_support", "streaming_tv", "streaming_movies",
    ]
    df["total_services"] = sum((df[c] == "Yes").astype(int) for c in addon_cols)

    # --- avg_monthly_spend_ratio ---------------------------------------------
    safe_tenure = df["tenure"].replace(0, 1)  # tenure=0 -> treat as 1 month
    df["avg_monthly_spend_ratio"] = (df["total_charges"] / safe_tenure).round(2)

    # --- high_risk_flag (short tenure + month-to-month + no tech support) ---
    df["high_risk_flag"] = (
        (df["tenure"] < 6)
        & (df["contract"] == "Month-to-month")
        & (df["tech_support"] == "No")
    ).astype(int)

    # --- payment_risk_flag (manual payment methods) --------------------------
    manual_methods = {"Electronic check", "Mailed check"}
    df["payment_risk_flag"] = df["payment_method"].isin(manual_methods).astype(int)

    # --- contract_ordinal (genuine order: MTM < 1yr < 2yr) -------------------
    contract_order = {"Month-to-month": 0, "One year": 1, "Two year": 2}
    df["contract_ordinal"] = df["contract"].map(contract_order)

    return df


# ----------------------------------------------------------------------------
# Columns used downstream (kept here so preprocessing.py / predict.py agree
# on exactly which columns feed the model).
# ----------------------------------------------------------------------------
NUMERIC_FEATURES = [
    "tenure", "monthly_charges", "total_charges",
    "total_services", "avg_monthly_spend_ratio", "contract_ordinal",
]

BINARY_FEATURES = [
    "senior_citizen", "partner", "dependents", "paperless_billing",
    "high_risk_flag", "payment_risk_flag",
]

NOMINAL_CATEGORICAL_FEATURES = [
    "gender", "internet_service", "payment_method", "tenure_group",
    "multiple_lines", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "phone_service",
]

ALL_MODEL_COLUMNS = NUMERIC_FEATURES + BINARY_FEATURES + NOMINAL_CATEGORICAL_FEATURES
