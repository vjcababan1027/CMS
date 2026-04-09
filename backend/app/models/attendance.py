from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    TARDY = "tardy"
    EXCUSED = "excused"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Teacher who recorded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_attendance_class_date", "class_id", "date"),
        Index("ix_attendance_student_class_date", "student_id", "class_id", "date"),
    )

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    class_obj = relationship("Class", back_populates="attendance_records")
    recorder = relationship("User", back_populates="attendance_records")
