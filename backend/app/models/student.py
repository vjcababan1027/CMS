from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    course = Column(String, nullable=False)
    year_level = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    class_code = Column(String, ForeignKey("classes.class_code"), nullable=True, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    parent_name = Column(String, nullable=True)
    parent_email = Column(String, nullable=True, index=True)
    parent_contact_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    parent_links = relationship("StudentParent", back_populates="student", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="student", cascade="all, delete-orphan")
