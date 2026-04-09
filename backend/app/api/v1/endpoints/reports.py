from collections import defaultdict
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.enrollment import Enrollment
from app.models.grade import Grade, GradingPeriod
from app.models.risk_prediction import RiskPrediction
from app.api.v1.endpoints.grades import _calculate_final_grade_logic
from app.schemas.report import StudentClassReport, PeriodGradeSummary, ClassPerformanceItem

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _authorize_class_access(class_obj: Class, current_user: User):
    if current_user.role == "admin":
        return
    if current_user.role == "teacher" and class_obj.teacher_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized for this class")


@router.get("/student/{student_id}/class/{class_id}", response_model=StudentClassReport)
def get_student_class_report(
    student_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    _authorize_class_access(class_obj, current_user)

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.class_id == class_id,
        Enrollment.is_active == True,  # noqa: E712
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is not actively enrolled in this class"
        )

    periods = [
        GradingPeriod.PRELIM,
        GradingPeriod.MIDTERM,
        GradingPeriod.SEMI_FINALS,
        GradingPeriod.FINALS,
    ]

    summaries: List[PeriodGradeSummary] = []
    for p in periods:
        calc = _calculate_final_grade_logic(student_id, class_id, p, db)
        summaries.append(
            PeriodGradeSummary(
                period=p.value,
                raw_grade=calc.raw_grade,
                transmuted_grade=calc.transmuted_grade,
                component_breakdown={k.value: v for k, v in calc.component_breakdown.items()},
            )
        )

    if summaries:
        overall_raw = sum(x.raw_grade for x in summaries) / len(summaries)
        overall_transmuted = sum(x.transmuted_grade for x in summaries) / len(summaries)
    else:
        overall_raw = 0.0
        overall_transmuted = 5.0

    return StudentClassReport(
        student_id=student_id,
        class_id=class_id,
        period_summaries=summaries,
        overall_raw_grade=overall_raw,
        overall_transmuted_grade=overall_transmuted,
    )


@router.get("/class/{class_id}/performance", response_model=List[ClassPerformanceItem])
def get_class_performance_report(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    _authorize_class_access(class_obj, current_user)

    active_enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.is_active == True,  # noqa: E712
    ).all()
    active_student_ids = {e.student_id for e in active_enrollments}

    grades = db.query(Grade).filter(Grade.class_id == class_id).all()
    by_student = defaultdict(list)
    for g in grades:
        if g.student_id in active_student_ids:
            by_student[g.student_id].append(g)

    students = db.query(Student).filter(Student.id.in_(active_student_ids)).all() if active_student_ids else []
    students_map = {s.id: s for s in students}

    results: List[ClassPerformanceItem] = []
    for student_id, student_grades in by_student.items():
        if not student_grades:
            continue
        avg_raw = sum(float(g.score) for g in student_grades) / len(student_grades)
        avg_transmuted = min(5.0, max(1.0, avg_raw / 20))

        latest_risk = db.query(RiskPrediction).filter(
            RiskPrediction.student_id == student_id,
            RiskPrediction.class_id == class_id
        ).order_by(RiskPrediction.prediction_date.desc()).first()

        student_obj = students_map.get(student_id)

        results.append(
            ClassPerformanceItem(
                student_id=student_id,
                student_code=student_obj.student_code if student_obj else None,
                student_name=student_obj.name if student_obj else None,
                average_raw_grade=avg_raw,
                average_transmuted_grade=avg_transmuted,
                latest_risk_level=latest_risk.risk_level.value if latest_risk else None,
            )
        )

    return sorted(results, key=lambda x: x.average_raw_grade)
