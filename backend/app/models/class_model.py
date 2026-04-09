from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    class_code = Column(String, unique=True, index=True, nullable=False)
    subject = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room = Column(String, nullable=True)
    academic_year = Column(String, nullable=False)
    term = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("User", back_populates="teacher_classes")
    enrollments = relationship("Enrollment", back_populates="class_obj", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="class_obj", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="class_obj", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="class_obj", cascade="all, delete-orphan")
    grade_weights = relationship("GradeWeight", back_populates="class_obj", cascade="all, delete-orphan")
