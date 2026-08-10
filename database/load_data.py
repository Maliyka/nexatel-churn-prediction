"""
load_data.py
============
Reads the raw Telco Customer Churn CSV extract and loads it into the
normalized PostgreSQL schema defined in schema.sql (customers, accounts,
services, churn_status).

Usage
-----
    # 1. Create the schema first:
    psql "$DATABASE_URL" -f database/schema.sql

    # 2. Then load the data:
    python database/load_data.py

Connection
----------
Reads the connection string from the DATABASE_URL environment variable
(see .env.example). Works unmodified against local Postgres, Supabase, or
Neon.tech — only the connection string changes.

    DATABASE_URL=postgresql://user:password@host:port/dbname
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

RAW_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "telco_churn_raw.csv")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nexatel_user:nexatel_dev_pw@localhost:5432/nexatel_churn")


def load_and_clean_csv(path: str) -> pd.DataFrame:
    """Load the raw CSV and apply the minimal cleaning needed to load it
    into typed SQL columns (deeper feature-engineering cleaning happens
    later in the pipeline, on purpose — this is the *database* layer)."""
    df = pd.read_csv(path)

    # TotalCharges ships as text with 11 blank entries (all tenure = 0
    # brand-new customers). Coerce to numeric; blanks become NaN -> SQL NULL.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Normalize Yes/No -> boolean for the columns that are truly binary.
    yes_no_cols = ["Partner", "Dependents", "PaperlessBilling"]
    for col in yes_no_cols:
        df[col] = df[col].map({"Yes": True, "No": False})

    df["SeniorCitizen"] = df["SeniorCitizen"].astype(bool)
    df["Churn"] = df["Churn"].map({"Yes": True, "No": False})

    # Sanity checks before we ever touch the database
    assert df["customerID"].is_unique, "Duplicate customerID found in raw extract!"
    assert df.shape[0] == 7043, f"Expected 7043 rows, found {df.shape[0]}"

    return df


def split_into_tables(df: pd.DataFrame):
    customers = df[["customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure"]].rename(
        columns={
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "Partner": "partner",
            "Dependents": "dependents",
        }
    )

    accounts = df[
        ["customerID", "Contract", "PaperlessBilling", "PaymentMethod", "MonthlyCharges", "TotalCharges"]
    ].rename(
        columns={
            "customerID": "customer_id",
            "Contract": "contract",
            "PaperlessBilling": "paperless_billing",
            "PaymentMethod": "payment_method",
            "MonthlyCharges": "monthly_charges",
            "TotalCharges": "total_charges",
        }
    )

    services = df[
        [
            "customerID", "PhoneService", "MultipleLines", "InternetService",
            "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
            "StreamingTV", "StreamingMovies",
        ]
    ].rename(
        columns={
            "customerID": "customer_id",
            "PhoneService": "phone_service",
            "MultipleLines": "multiple_lines",
            "InternetService": "internet_service",
            "OnlineSecurity": "online_security",
            "OnlineBackup": "online_backup",
            "DeviceProtection": "device_protection",
            "TechSupport": "tech_support",
            "StreamingTV": "streaming_tv",
            "StreamingMovies": "streaming_movies",
        }
    )

    churn_status = df[["customerID", "Churn"]].rename(columns={"customerID": "customer_id", "Churn": "churn"})

    return customers, accounts, services, churn_status


def main():
    print(f"Reading raw CSV from {RAW_CSV_PATH} ...")
    df = load_and_clean_csv(RAW_CSV_PATH)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns.")

    customers, accounts, services, churn_status = split_into_tables(df)

    print(f"Connecting to {DATABASE_URL.split('@')[-1]} ...")
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        # Truncate first so this script is safely re-runnable
        conn.execute(text("TRUNCATE churn_status, services, accounts, customers CASCADE;"))

    tables = {
        "customers": customers,
        "accounts": accounts,
        "services": services,
        "churn_status": churn_status,
    }

    for name, table_df in tables.items():
        table_df.to_sql(name, engine, if_exists="append", index=False, method="multi", chunksize=500)
        print(f"  Loaded {len(table_df):>5} rows -> {name}")

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM v_customer_360")).scalar()
        print(f"\nVerification: v_customer_360 view returns {count} joined rows.")
        if count != len(df):
            print("WARNING: joined row count does not match source row count — check for orphaned rows.", file=sys.stderr)

    print("\nDone. Data loaded into normalized schema.")


if __name__ == "__main__":
    main()
