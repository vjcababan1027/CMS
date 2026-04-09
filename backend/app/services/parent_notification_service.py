from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.student import Student
from app.models.risk_prediction import RiskPrediction, RiskLevel


def ensure_parent_email_logs_table(db: Session):
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


def _send_email(to_email: str, subject: str, body: str) -> bool:
    if settings.SMTP_MOCK_MODE or not settings.SMTP_HOST:
        return True

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


def _insert_log(
    db: Session,
    student_id: int,
    parent_email: str,
    period: str,
    attendance_summary: str,
    risk_level: str,
    teacher_remarks: str,
    status: str,
):
    sent_at = datetime.utcnow() if status == "success" else None
    db.execute(
        text(
            """
            INSERT INTO parent_email_logs
                (student_id, parent_email, period, attendance_summary, risk_level, teacher_remarks, status, sent_at)
            VALUES
                (:student_id, :parent_email, :period, :attendance_summary, :risk_level, :teacher_remarks, :status, :sent_at)
            """
        ),
        {
            "student_id": student_id,
            "parent_email": parent_email,
            "period": period,
            "attendance_summary": attendance_summary,
            "risk_level": risk_level,
            "teacher_remarks": teacher_remarks,
            "status": status,
            "sent_at": sent_at,
        },
    )


def _build_student_report_context(db: Session, student: Student):
    latest_risk = db.query(RiskPrediction).filter(
        RiskPrediction.student_id == student.id,
        RiskPrediction.is_active == True
    ).order_by(RiskPrediction.prediction_date.desc()).first()

    risk_level = latest_risk.risk_level.value if latest_risk else "low"
    period = latest_risk.period.value if latest_risk else "prelim"

    attendance_rows = db.execute(
        text(
            """
            SELECT status, COUNT(*) as cnt
            FROM attendance
            WHERE student_id = :student_id
            GROUP BY status
            """
        ),
        {"student_id": student.id},
    ).mappings().all()

    counts = {r["status"]: int(r["cnt"]) for r in attendance_rows}
    attendance_summary = (
        f"Present: {counts.get('present', 0)}, "
        f"Absent: {counts.get('absent', 0)}, "
        f"Tardy: {counts.get('tardy', 0)}, "
        f"Excused: {counts.get('excused', 0)}"
    )

    remarks = "Keep up the good work."
    if risk_level == RiskLevel.HIGH.value:
        remarks = "Immediate intervention is recommended."
    elif risk_level == RiskLevel.MODERATE.value:
        remarks = "Please monitor academic progress closely."

    return period, risk_level, attendance_summary, remarks


def _resolve_parent_email(db: Session, student: Student):

    row = db.execute(
        text(
            """
            SELECT p.email
            FROM student_parents sp
            JOIN parents p ON p.id = sp.parent_id
            WHERE sp.student_id = :student_id
            ORDER BY p.id ASC
            LIMIT 1
            """
        ),
        {"student_id": student.id},
    ).mappings().first()
    return row["email"] if row and row.get("email") else None


def dispatch_for_student(db: Session, student: Student):
    parent_email = _resolve_parent_email(db, student)
    if not parent_email:
        return {"student_id": student.id, "status": "skipped_no_parent_email"}

    period, risk_level, attendance_summary, remarks = _build_student_report_context(db, student)

    subject = f"Student Performance Update - {student.first_name} {student.last_name}"
    body = (
        f"Student: {student.first_name} {student.last_name}\n"
        f"Period: {period}\n"
        f"Risk Level: {risk_level}\n"
        f"Attendance: {attendance_summary}\n"
        f"Teacher Remarks: {remarks}\n"
    )

    sent = _send_email(parent_email, subject, body)
    status = "success" if sent else "failed"

    _insert_log(
        db=db,
        student_id=student.id,
        parent_email=parent_email,
        period=period,
        attendance_summary=attendance_summary,
        risk_level=risk_level,
        teacher_remarks=remarks,
        status=status,
    )
    return {"student_id": student.id, "status": status}


def run_biweekly_dispatch(db: Session):
    ensure_parent_email_logs_table(db)
    students = db.query(Student).filter(Student.is_active == True).all()

    results = []
    for s in students:
        results.append(dispatch_for_student(db, s))

    db.commit()
    return {"mode": "biweekly", "count": len(results), "results": results}


def run_high_risk_dispatch(db: Session):
    ensure_parent_email_logs_table(db)

    high_risk_rows = db.query(RiskPrediction).filter(
        RiskPrediction.risk_level == RiskLevel.HIGH,
        RiskPrediction.is_active == True
    ).order_by(RiskPrediction.prediction_date.desc()).all()

    seen_students = set()
    results = []
    for row in high_risk_rows:
        if row.student_id in seen_students:
            continue
        seen_students.add(row.student_id)

        student = db.query(Student).filter(Student.id == row.student_id).first()
        if not student or not student.is_active:
            continue
        results.append(dispatch_for_student(db, student))

    db.commit()
    return {"mode": "high_risk", "count": len(results), "results": results}
