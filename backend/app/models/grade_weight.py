from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class GradeWeight(Base):
    __tablename__ = "grade_weights"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    period = Column(String, nullable=False)  # prelim, midterm, semi_finals, finals
    quizzes_weight = Column(Float, default=0.20)  # 20%
    oral_participation_weight = Column(Float, default=0.10)  # 10%
    graded_activity_weight = Column(Float, default=0.20)  # 20%
    attendance_weight = Column(Float, default=0.10)  # 10%
    major_exam_weight = Column(Float, default=0.40)  # 40%
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure one weight configuration per class per period
    __table_args__ = (UniqueConstraint('class_id', 'period', name='_class_period_uc'),)

    # Relationships
    class_obj = relationship("Class", back_populates="grade_weights")
