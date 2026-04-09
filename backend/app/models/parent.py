from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    relationship_to_student = Column(String, nullable=False)  # mother, father, guardian
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Linked user account if they have one
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="parent_students")
    student_links = relationship("StudentParent", back_populates="parent", cascade="all, delete-orphan")
