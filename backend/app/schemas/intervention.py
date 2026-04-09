from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from app.schemas.risk_prediction import RiskPrediction as RiskPredictionSchema


InterventionCategory = Literal[
    "remedial",
    "extra_assignments",
    "counseling",
    "parent_notification",
    "monitoring",
]


class InterventionRecommendation(BaseModel):
    category: InterventionCategory
    action: str
    priority: int = Field(..., ge=1, le=5)  # 1 highest, 5 lowest
    rationale: Optional[str] = None


class InterventionPlanResponse(BaseModel):
    student_id: int
    class_id: int
    generated_at: datetime
    prediction: RiskPredictionSchema
    recommendations: List[InterventionRecommendation]
