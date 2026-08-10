"""
app/main.py
============
FastAPI backend for the NexaTel Churn Prediction & Retention Intelligence
System. Exposes:

  GET  /health            - liveness check (used by Render + the frontend)
  POST /predict            - score a single customer, return risk + reasons
  GET  /dashboard-stats    - pre-computed EDA headline numbers, for the
                              frontend's "Insights" tab (Phase 7, bonus)

Run locally:
    uvicorn app.main:app --reload --port 8000

CORS: origin allow-list is read from the ALLOWED_ORIGINS env var (comma
separated) so the deployed frontend URL can be added without a code change.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import CustomerInput, PredictionResponse
from app.predict import predict_customer

app = FastAPI(
    title="NexaTel Churn Prediction API",
    description="Predicts customer churn risk and explains the top drivers behind each score.",
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerInput):
    try:
        result = predict_customer(customer.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# Headline numbers from Phase 1/2 (SQL + EDA), hard-coded from the executed
# notebooks so the dashboard tab loads instantly with no DB round-trip.
# In a production system these would be refreshed by a scheduled job that
# re-runs queries.sql against the live database.
DASHBOARD_STATS = {
    "overall_churn_rate_pct": 26.54,
    "total_customers": 7043,
    "churned_customers": 1869,
    "monthly_revenue_at_risk": 139130.85,
    "annualized_revenue_at_risk": 1669570.20,
    "churn_by_contract": [
        {"contract": "Month-to-month", "churn_rate_pct": 42.71},
        {"contract": "One year", "churn_rate_pct": 11.27},
        {"contract": "Two year", "churn_rate_pct": 2.83},
    ],
    "churn_by_internet_service": [
        {"internet_service": "Fiber optic", "churn_rate_pct": 41.89},
        {"internet_service": "DSL", "churn_rate_pct": 18.96},
        {"internet_service": "No internet", "churn_rate_pct": 7.40},
    ],
    "highest_risk_segment": {
        "description": "Tenure < 6 months, Month-to-month contract, no tech support",
        "churn_rate_pct": 66.52,
        "segment_size": 908,
    },
    "model_name": "Logistic Regression (SMOTE-balanced)",
    "model_recall_pct": 79.14,
    "model_f1_pct": 62.32,
    "model_roc_auc_pct": 83.68,
}


@app.get("/dashboard-stats")
def dashboard_stats():
    return DASHBOARD_STATS


@app.get("/")
def root():
    return {
        "message": "NexaTel Churn Prediction API is running.",
        "docs": "/docs",
        "endpoints": ["/health", "/predict", "/dashboard-stats"],
    }
