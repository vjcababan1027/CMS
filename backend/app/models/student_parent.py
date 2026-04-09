from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class StudentParent(Base):
    __tablename__ = "student_parents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    is_primary_contact = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="parent_links")
    parent = relationship("Parent", back_populates="student_links")
