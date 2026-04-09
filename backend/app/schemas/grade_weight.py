from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GradeWeightBase(BaseModel):
    class_id: int
    period: str = Field(..., pattern="^(prelim|midterm|semi_finals|finals)$")
    quizzes_weight: float = Field(..., ge=0.0, le=1.0)
    oral_participation_weight: float = Field(..., ge=0.0, le=1.0)
    graded_activity_weight: float = Field(..., ge=0.0, le=1.0)
    attendance_weight: float = Field(..., ge=0.0, le=1.0)
    major_exam_weight: float = Field(..., ge=0.0, le=1.0)


class GradeWeightCreate(GradeWeightBase):
    pass


class GradeWeightUpdate(BaseModel):
    period: Optional[str] = Field(default=None, pattern="^(prelim|midterm|semi_finals|finals)$")
    quizzes_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    oral_participation_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    graded_activity_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    attendance_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    major_exam_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class GradeWeight(GradeWeightBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
