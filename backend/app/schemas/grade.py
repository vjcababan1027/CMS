from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from app.models.grade import GradeComponent, GradingPeriod

class GradeComponent(str, Enum):
    QUIZZES = "quizzes"
    ORAL_PARTICIPATION = "oral_participation"
    GRADED_ACTIVITY = "graded_activity"
    ATTENDANCE = "attendance"
    MAJOR_EXAM = "major_exam"

class GradingPeriod(str, Enum):
    PRELIM = "prelim"
    MIDTERM = "midterm"
    SEMI_FINALS = "semi_finals"
    FINALS = "finals"

class GradeBase(BaseModel):
    student_id: int
    class_id: int
    component: GradeComponent
    period: GradingPeriod
    score: float
    max_score: Optional[float] = 100.0
    weight_percentage: Optional[float] = None

class GradeCreate(BaseModel):
    student_id: Optional[int] = None
    student_code: Optional[str] = None
    class_id: Optional[int] = None
    class_code: Optional[str] = None
    component: GradeComponent
    period: GradingPeriod
    score: float
    max_score: Optional[float] = 100.0
    weight_percentage: Optional[float] = None

class GradeUpdate(BaseModel):
    student_id: Optional[int] = None
    student_code: Optional[str] = None
    class_id: Optional[int] = None
    class_code: Optional[str] = None
    component: Optional[GradeComponent] = None
    period: Optional[GradingPeriod] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    weight_percentage: Optional[float] = None

class Grade(GradeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GradeCalculation(BaseModel):
    student_id: int
    class_id: int
    period: GradingPeriod
    raw_grade: float
    transmuted_grade: float
    component_breakdown: Dict[GradeComponent, Dict[str, float]]

    class Config:
        from_attributes = True

class ClassPeriodGradeSummaryItem(BaseModel):
    student_id: int
    student_code: str
    student_name: str
    raw_grade: float
    transmuted_grade: float

class ClassPeriodGradeSummary(BaseModel):
    class_id: int
    class_code: str
    period: GradingPeriod
    total_students: int
    results: List[ClassPeriodGradeSummaryItem]
