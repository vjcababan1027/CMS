from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class GradeComponent(str, enum.Enum):
    QUIZZES = "quizzes"
    ORAL_PARTICIPATION = "oral_participation"
    GRADED_ACTIVITY = "graded_activity"
    ATTENDANCE = "attendance"
    MAJOR_EXAM = "major_exam"

class GradingPeriod(str, enum.Enum):
    PRELIM = "prelim"
    MIDTERM = "midterm"
    SEMI_FINALS = "semi_finals"
    FINALS = "finals"

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    component = Column(Enum(GradeComponent), nullable=False)
    period = Column(Enum(GradingPeriod), nullable=False)
    score = Column(Float, nullable=False)  # Raw score (0-100)
    max_score = Column(Float, default=100.0)
    weight_percentage = Column(Float, nullable=False)  # Weight for this component
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_grades_class_period", "class_id", "period"),
        Index("ix_grades_student_class_period", "student_id", "class_id", "period"),
    )

    # Relationships
    student = relationship("Student", back_populates="grades")
    class_obj = relationship("Class", back_populates="grades")
