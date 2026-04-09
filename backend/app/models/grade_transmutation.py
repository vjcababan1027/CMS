from sqlalchemy import Column, Integer, String, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class GradeTransmutation(Base):
    __tablename__ = "grade_transmutations"

    id = Column(Integer, primary_key=True, index=True)
    raw_grade_min = Column(Float, nullable=False)  # Inclusive lower bound
    raw_grade_max = Column(Float, nullable=False)  # Exclusive upper bound (except for max)
    transmuted_grade = Column(Float, nullable=False)  # 1.0 - 5.0 scale
    description = Column(String, nullable=True)  # e.g., "Excellent", "Satisfactory"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure no overlapping ranges
    __table_args__ = (
        UniqueConstraint('raw_grade_min', 'raw_grade_max', name='_grade_range_uc'),
    )