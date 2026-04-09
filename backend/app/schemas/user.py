from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str  # admin, teacher

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"admin", "teacher"}
        if normalized not in allowed:
            raise ValueError("role must be either 'admin' or 'teacher'")
        return normalized

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None