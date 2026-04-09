from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.models.class_model import Class
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.attendance import (
    AttendanceCreate,
    Attendance as AttendanceSchema,
    AttendanceUpdate,
    AttendanceBulkCreateItem,
    AttendanceDailySummary,
)
from app.core import security
from datetime import date, datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _resolve_student(db: Session, student_id: Optional[int], student_code: Optional[str]) -> Student:
    if student_id is not None:
        student = db.query(Student).filter(Student.id == student_id).first()
    elif student_code:
        student = db.query(Student).filter(Student.student_id == student_code).first()
    else:
        raise HTTPException(status_code=400, detail="Provide either student_id or student_code")
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not student.is_active:
        raise HTTPException(status_code=400, detail="Student is inactive")
    return student

def _resolve_class(db: Session, class_id: Optional[int], class_code: Optional[str]) -> Class:
    if class_id is not None:
        class_obj = db.query(Class).filter(Class.id == class_id).first()
    elif class_code:
        class_obj = db.query(Class).filter(Class.class_code == class_code).first()
    else:
        raise HTTPException(status_code=400, detail="Provide either class_id or class_code")
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

def _authorize_teacher_or_admin_for_class(current_user: User, class_obj: Class):
    if current_user.role == "admin":
        return
    if current_user.role == "teacher" and class_obj.teacher_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not allowed to manage attendance for this class")

def _validate_active_enrollment(db: Session, student: Student, class_obj: Class):
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.class_id == class_obj.id,
        Enrollment.is_active == True,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student is not actively enrolled in this class")

@router.get("/", response_model=List[AttendanceSchema])
def read_attendance(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    query = db.query(Attendance)

    if current_user.role == "teacher":
        query = query.join(Class, Class.id == Attendance.class_id).filter(Class.teacher_id == current_user.id)

    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    attendance = query.offset(skip).limit(limit).all()
    return attendance

@router.post("/bulk", response_model=List[AttendanceSchema])
def create_bulk_attendance(
    attendance_records: List[AttendanceBulkCreateItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    created_records = []
    for record_in in attendance_records:
        student = _resolve_student(db, record_in.student_id, record_in.student_code)
        class_obj = _resolve_class(db, record_in.class_id, record_in.class_code)
        _authorize_teacher_or_admin_for_class(current_user, class_obj)
        _validate_active_enrollment(db, student, class_obj)

        existing = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.class_id == class_obj.id,
            Attendance.date == record_in.date
        ).first()

        if existing:
            existing.status = record_in.status
            existing.recorded_by = current_user.id
            db.add(existing)
            created_records.append(existing)
        else:
            attendance = Attendance(
                student_id=student.id,
                class_id=class_obj.id,
                date=record_in.date,
                status=record_in.status,
                recorded_by=current_user.id,
            )
            db.add(attendance)
            created_records.append(attendance)

    db.commit()
    for record in created_records:
        db.refresh(record)
    return created_records

@router.get("/summary/daily", response_model=AttendanceDailySummary)
def get_daily_attendance_summary(
    class_id: Optional[int] = None,
    class_code: Optional[str] = None,
    target_date: date = Depends(lambda: date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    class_obj = _resolve_class(db, class_id, class_code)
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())

    records = db.query(Attendance).filter(
        Attendance.class_id == class_obj.id,
        Attendance.date >= start_dt,
        Attendance.date <= end_dt
    ).all()

    return AttendanceDailySummary(
        class_id=class_obj.id,
        class_code=class_obj.class_code,
        date=start_dt,
        total_records=len(records),
        present=sum(1 for r in records if r.status == AttendanceStatus.PRESENT),
        absent=sum(1 for r in records if r.status == AttendanceStatus.ABSENT),
        tardy=sum(1 for r in records if r.status == AttendanceStatus.TARDY),
        excused=sum(1 for r in records if r.status == AttendanceStatus.EXCUSED),
    )

@router.get("/{attendance_id}", response_model=AttendanceSchema)
def read_attendance_record(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    class_obj = db.query(Class).filter(Class.id == attendance.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    return attendance

@router.post("/", response_model=AttendanceSchema)
def create_attendance_record(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = _resolve_student(db, attendance_in.student_id, attendance_in.student_code)
    class_obj = _resolve_class(db, attendance_in.class_id, attendance_in.class_code)
    _authorize_teacher_or_admin_for_class(current_user, class_obj)
    _validate_active_enrollment(db, student, class_obj)

    existing = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_obj.id,
        Attendance.date == attendance_in.date
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance record already exists for this student/class/date"
        )

    attendance = Attendance(
        student_id=student.id,
        class_id=class_obj.id,
        date=attendance_in.date,
        status=attendance_in.status,
        recorded_by=current_user.id,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceSchema)
def update_attendance_record(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    update_data = attendance_in.dict(exclude_unset=True)

    new_student = _resolve_student(
        db,
        update_data.get("student_id", attendance.student_id),
        update_data.get("student_code", None),
    )
    new_class = _resolve_class(
        db,
        update_data.get("class_id", attendance.class_id),
        update_data.get("class_code", None),
    )
    _authorize_teacher_or_admin_for_class(current_user, new_class)
    _validate_active_enrollment(db, new_student, new_class)

    new_date = update_data.get("date", attendance.date)

    duplicate = db.query(Attendance).filter(
        Attendance.student_id == new_student.id,
        Attendance.class_id == new_class.id,
        Attendance.date == new_date,
        Attendance.id != attendance_id
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Attendance record already exists for this student/class/date"
        )

    attendance.student_id = new_student.id
    attendance.class_id = new_class.id
    if "date" in update_data:
        attendance.date = update_data["date"]
    if "status" in update_data:
        attendance.status = update_data["status"]
    attendance.recorded_by = current_user.id

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_record(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    class_obj = db.query(Class).filter(Class.id == attendance.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    db.delete(attendance)
    db.commit()
    return {"ok": True}
