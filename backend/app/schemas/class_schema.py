from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.student import Student as StudentSchema

class ClassBase(BaseModel):
    name: str
    class_code: str
    subject: str
    teacher_id: int
    room: Optional[str] = None
    academic_year: str
    term: str
    is_active: Optional[bool] = True

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    class_code: Optional[str] = None
    subject: Optional[str] = None
    teacher_id: Optional[int] = None
    room: Optional[str] = None
    academic_year: Optional[str] = None
    term: Optional[str] = None
    is_active: Optional[bool] = None

class Class(ClassBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClassRosterResponse(BaseModel):
    class_code: str
    class_name: str
    total_students: int
    students: list[StudentSchema]

class EnrollmentActionResponse(BaseModel):
    message: str
    class_code: str
    student_id: str
    enrollment_active: bool
