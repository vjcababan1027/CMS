from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Float, nullable=False)  # Probability 0-1
    risk_level = Column(Enum(RiskLevel), nullable=False)
    features_used = Column(String, nullable=True)  # JSON string of features
    model_version = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_risk_predictions_class_active_date", "class_id", "is_active", "prediction_date"),
        Index("ix_risk_predictions_student_class_date", "student_id", "class_id", "prediction_date"),
    )

    # Relationships
    student = relationship("Student", back_populates="risk_predictions")
    class_obj = relationship("Class", back_populates="risk_predictions")
