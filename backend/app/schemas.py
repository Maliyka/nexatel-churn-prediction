"""
app/schemas.py
================
Pydantic models for the /predict endpoint. Field names match the database
schema (snake_case) so the same customer record can flow: DB -> notebook ->
API with no renaming step.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class CustomerInput(BaseModel):
    gender: Literal["Male", "Female"]
    senior_citizen: bool = False
    partner: bool = False
    dependents: bool = False
    tenure: int = Field(ge=0, le=100, description="Months as a customer")

    phone_service: Literal["Yes", "No"] = "Yes"
    multiple_lines: Literal["Yes", "No", "No phone service"] = "No"
    internet_service: Literal["DSL", "Fiber optic", "No"]
    online_security: Literal["Yes", "No", "No internet service"] = "No"
    online_backup: Literal["Yes", "No", "No internet service"] = "No"
    device_protection: Literal["Yes", "No", "No internet service"] = "No"
    tech_support: Literal["Yes", "No", "No internet service"] = "No"
    streaming_tv: Literal["Yes", "No", "No internet service"] = "No"
    streaming_movies: Literal["Yes", "No", "No internet service"] = "No"

    contract: Literal["Month-to-month", "One year", "Two year"]
    paperless_billing: bool = True
    payment_method: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ]
    monthly_charges: float = Field(ge=0)
    total_charges: Optional[float] = Field(default=None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "senior_citizen": False,
                "partner": True,
                "dependents": False,
                "tenure": 2,
                "phone_service": "Yes",
                "multiple_lines": "No",
                "internet_service": "Fiber optic",
                "online_security": "No",
                "online_backup": "No",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "No",
                "streaming_movies": "No",
                "contract": "Month-to-month",
                "paperless_billing": True,
                "payment_method": "Electronic check",
                "monthly_charges": 85.5,
                "total_charges": 171.0,
            }
        }


class Reason(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    churn_probability: float
    risk_level: Literal["Low", "Medium", "High"]
    top_reasons: list[Reason]
    suggested_action: str
    model_name: str
