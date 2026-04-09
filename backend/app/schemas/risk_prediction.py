from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.risk_prediction import RiskLevel


class RiskPredictionBase(BaseModel):
    student_id: int
    class_id: int
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    features_used: Optional[str] = None
    model_version: Optional[str] = None
    is_active: bool = True


class RiskPredictionCreate(RiskPredictionBase):
    pass


class RiskPredictionUpdate(BaseModel):
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    risk_level: Optional[RiskLevel] = None
    features_used: Optional[str] = None
    model_version: Optional[str] = None
    is_active: Optional[bool] = None


class RiskPrediction(RiskPredictionBase):
    id: int
    prediction_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
