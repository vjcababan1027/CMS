from typing import Dict, List, Optional
from pydantic import BaseModel


class PeriodGradeSummary(BaseModel):
    period: str
    raw_grade: float
    transmuted_grade: float
    component_breakdown: Dict[str, Dict[str, float]]


class StudentClassReport(BaseModel):
    student_id: int
    class_id: int
    period_summaries: List[PeriodGradeSummary]
    overall_raw_grade: float
    overall_transmuted_grade: float


class ClassPerformanceItem(BaseModel):
    student_id: int
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    average_raw_grade: float
    average_transmuted_grade: float
    latest_risk_level: Optional[str] = None
