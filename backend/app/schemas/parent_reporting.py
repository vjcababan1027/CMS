from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ParentEmailLogBase(BaseModel):
    student_id: int
    parent_email: EmailStr
    period: str
    attendance_summary: Optional[str] = None
    risk_level: Optional[str] = None
    teacher_remarks: Optional[str] = None
    status: str = "pending"


class ParentEmailLogCreate(ParentEmailLogBase):
    pass


class ParentEmailLogUpdate(BaseModel):
    attendance_summary: Optional[str] = None
    risk_level: Optional[str] = None
    teacher_remarks: Optional[str] = None
    status: Optional[str] = None


class ParentEmailLog(ParentEmailLogBase):
    id: int
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
