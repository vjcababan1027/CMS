from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure a student can only be enrolled once in a class
    __table_args__ = (UniqueConstraint('student_id', 'class_id', name='_student_class_uc'),)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    class_obj = relationship("Class", back_populates="enrollments")
