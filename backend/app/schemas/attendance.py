from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    TARDY = "tardy"
    EXCUSED = "excused"

class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: datetime
    status: AttendanceStatus
    recorded_by: int

class AttendanceCreate(BaseModel):
    student_id: Optional[int] = None
    student_code: Optional[str] = None
    class_id: Optional[int] = None
    class_code: Optional[str] = None
    date: datetime
    status: AttendanceStatus

class AttendanceBulkCreateItem(BaseModel):
    student_id: Optional[int] = None
    student_code: Optional[str] = None
    class_id: Optional[int] = None
    class_code: Optional[str] = None
    date: datetime
    status: AttendanceStatus

class AttendanceUpdate(BaseModel):
    student_id: Optional[int] = None
    student_code: Optional[str] = None
    class_id: Optional[int] = None
    class_code: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None

class Attendance(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AttendanceDailySummary(BaseModel):
    class_id: int
    class_code: str
    date: datetime
    total_records: int
    present: int
    absent: int
    tardy: int
    excused: int
