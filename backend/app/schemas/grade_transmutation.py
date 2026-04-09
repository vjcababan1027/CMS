from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GradeTransmutationBase(BaseModel):
    raw_grade_min: float = Field(..., ge=0, le=100)
    raw_grade_max: float = Field(..., ge=0, le=100)
    transmuted_grade: float = Field(..., ge=1.0, le=5.0)
    description: Optional[str] = None


class GradeTransmutationCreate(GradeTransmutationBase):
    pass


class GradeTransmutationUpdate(BaseModel):
    raw_grade_min: Optional[float] = Field(default=None, ge=0, le=100)
    raw_grade_max: Optional[float] = Field(default=None, ge=0, le=100)
    transmuted_grade: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    description: Optional[str] = None


class GradeTransmutation(GradeTransmutationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GradeTransmutationConversion(BaseModel):
    raw_grade: float
    transmuted_grade: float
    raw_grade_min: Optional[float] = None
    raw_grade_max: Optional[float] = None
    description: Optional[str] = None
