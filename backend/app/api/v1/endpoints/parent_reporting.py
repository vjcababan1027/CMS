from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.student import Student
from app.schemas.parent_reporting import (
    ParentEmailLog,
    ParentEmailLogCreate,
    ParentEmailLogUpdate,
)
from app.core import security
from app.models.user import User
from app.services.parent_notification_service import (
    run_biweekly_dispatch,
    run_high_risk_dispatch,
)

router = APIRouter()

ALLOWED_STATUSES = {"pending", "success", "failed"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_table(db: Session):
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parent_email_logs (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                parent_email VARCHAR NOT NULL,
                period VARCHAR NOT NULL,
                attendance_summary VARCHAR NULL,
                risk_level VARCHAR NULL,
                teacher_remarks VARCHAR NULL,
                status VARCHAR NOT NULL DEFAULT 'pending',
                sent_at TIMESTAMPTZ NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.commit()


def _normalize_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {sorted(ALLOWED_STATUSES)}"
        )
    return normalized


@router.get("/", response_model=List[ParentEmailLog])
def list_parent_email_logs(
    student_id: Optional[int] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(security.get_current_teacher_or_admin),
):
    ensure_table(db)

    where_clauses = []
    params = {}

    if student_id is not None:
        where_clauses.append("student_id = :student_id")
        params["student_id"] = student_id

    if status_filter is not None:
        normalized_status = _normalize_status(status_filter)
        where_clauses.append("LOWER(status) = :status")
        params["status"] = normalized_status

    if period is not None:
        where_clauses.append("LOWER(period) = :period")
        params["period"] = period.strip().lower()

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    rows = db.execute(
        text(
            f"""
            SELECT id, student_id, parent_email, period, attendance_summary, risk_level,
                   teacher_remarks, status, sent_at, created_at
            FROM parent_email_logs
            {where_sql}
            ORDER BY id DESC
            """
        ),
        params,
    ).mappings().all()
    return [ParentEmailLog(**dict(r)) for r in rows]


@router.post("/", response_model=ParentEmailLog, status_code=status.HTTP_201_CREATED)
def create_parent_email_log(
    payload: ParentEmailLogCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(security.get_current_admin),
):
    ensure_table(db)

    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    normalized_status = _normalize_status(payload.status)
    sent_at = datetime.utcnow() if normalized_status == "success" else None

    row = db.execute(
        text(
            """
            INSERT INTO parent_email_logs
                (student_id, parent_email, period, attendance_summary, risk_level, teacher_remarks, status, sent_at)
            VALUES
                (:student_id, :parent_email, :period, :attendance_summary, :risk_level, :teacher_remarks, :status, :sent_at)
            RETURNING id, student_id, parent_email, period, attendance_summary, risk_level,
                      teacher_remarks, status, sent_at, created_at
            """
        ),
        {
            "student_id": payload.student_id,
            "parent_email": payload.parent_email,
            "period": payload.period,
            "attendance_summary": payload.attendance_summary,
            "risk_level": payload.risk_level,
            "teacher_remarks": payload.teacher_remarks,
            "status": normalized_status,
            "sent_at": sent_at,
        },
    ).mappings().first()

    db.commit()
    return ParentEmailLog(**dict(row))


@router.put("/{log_id}", response_model=ParentEmailLog)
def update_parent_email_log(
    log_id: int,
    payload: ParentEmailLogUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(security.get_current_admin),
):
    ensure_table(db)

    existing = db.execute(
        text("SELECT id, sent_at, status FROM parent_email_logs WHERE id = :id"),
        {"id": log_id},
    ).mappings().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Parent email log not found")

    update_data = payload.dict(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        normalized_status = _normalize_status(update_data["status"])
        update_data["status"] = normalized_status
        if normalized_status == "success":
            update_data["sent_at"] = datetime.utcnow()
        elif normalized_status in {"pending", "failed"}:
            update_data["sent_at"] = None

    if update_data:
        sets = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_data["id"] = log_id
        db.execute(
            text(f"UPDATE parent_email_logs SET {sets} WHERE id = :id"),
            update_data,
        )
        db.commit()

    row = db.execute(
        text(
            """
            SELECT id, student_id, parent_email, period, attendance_summary, risk_level,
                   teacher_remarks, status, sent_at, created_at
            FROM parent_email_logs
            WHERE id = :id
            """
        ),
        {"id": log_id},
    ).mappings().first()

    return ParentEmailLog(**dict(row))


@router.post("/trigger/biweekly")
def trigger_biweekly_parent_notifications(
    db: Session = Depends(get_db),
    _current_user: User = Depends(security.get_current_admin),
):
    ensure_table(db)
    return run_biweekly_dispatch(db)


@router.post("/trigger/high-risk")
def trigger_high_risk_parent_notifications(
    db: Session = Depends(get_db),
    _current_user: User = Depends(security.get_current_admin),
):
    ensure_table(db)
    return run_high_risk_dispatch(db)
