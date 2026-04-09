from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    course: str
    year_level: int
    section: str
    class_code: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    parent_contact_number: Optional[str] = None
    is_active: Optional[bool] = True

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    student_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    course: Optional[str] = None
    year_level: Optional[int] = None
    section: Optional[str] = None
    class_code: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    parent_contact_number: Optional[str] = None
    is_active: Optional[bool] = None

class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
