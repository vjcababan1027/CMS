import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.models.risk_prediction import RiskPrediction, RiskLevel
from app.models.student import Student
from app.models.class_model import Class
from app.models.user import User
from app.models.enrollment import Enrollment
from app.models.grade import Grade, GradingPeriod
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.risk_prediction import (
    RiskPrediction as RiskPredictionSchema,
    RiskPredictionCreate,
    RiskPredictionUpdate,
)

router = APIRouter()

RISK_MODEL_VERSION = "heuristic-v1"


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


def _ensure_active_enrollment(db: Session, student_id: int, class_id: int):
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


def _safe_json_loads(text: Optional[str]) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def _safe_json_dumps(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, separators=(",", ":"), default=str)


def _compute_risk_features(
    db: Session,
    student_id: int,
    class_id: int,
    period: Optional[GradingPeriod] = None,
) -> Dict[str, Any]:
    # Grades
    grades_query = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.class_id == class_id,
    )
    if period is not None:
        grades_query = grades_query.filter(Grade.grading_period == period)
    grades = grades_query.all()

    grade_scores = [float(g.score) for g in grades]
    avg_grade = (sum(grade_scores) / len(grade_scores)) if grade_scores else 0.0

    expected_components = 5  # Quizzes/Oral/Activity/Attendance/Major Exam
    grade_completeness = min(1.0, len(grades) / expected_components) if expected_components else 1.0
    missing_grade_ratio = max(0.0, 1.0 - grade_completeness)

    # Attendance
    attendance_query = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.class_id == class_id,
    )
    attendance_records = attendance_query.all()
    total_attendance = len(attendance_records)
    present_count = sum(1 for a in attendance_records if a.status == AttendanceStatus.PRESENT)
    late_count = sum(1 for a in attendance_records if a.status == AttendanceStatus.LATE)
    absent_count = sum(1 for a in attendance_records if a.status == AttendanceStatus.ABSENT)

    present_ratio = (present_count / total_attendance) if total_attendance else 1.0
    absent_ratio = (absent_count / total_attendance) if total_attendance else 0.0
    late_ratio = (late_count / total_attendance) if total_attendance else 0.0

    features = {
        "period": period.value if period is not None else None,
        "avg_grade": round(avg_grade, 4),
        "grade_count": len(grades),
        "grade_completeness": round(grade_completeness, 4),
        "missing_grade_ratio": round(missing_grade_ratio, 4),
        "attendance_count": total_attendance,
        "present_ratio": round(present_ratio, 4),
        "late_ratio": round(late_ratio, 4),
        "absent_ratio": round(absent_ratio, 4),
    }
    return features


def _score_from_features(features: Dict[str, Any]) -> float:
    avg_grade = float(features.get("avg_grade", 0.0))
    missing_grade_ratio = float(features.get("missing_grade_ratio", 0.0))
    absent_ratio = float(features.get("absent_ratio", 0.0))
    late_ratio = float(features.get("late_ratio", 0.0))

    grade_risk = max(0.0, min(1.0, (75.0 - avg_grade) / 75.0))
    attendance_risk = max(0.0, min(1.0, absent_ratio + (late_ratio * 0.5)))
    completeness_risk = max(0.0, min(1.0, missing_grade_ratio))

    risk_score = (
        grade_risk * 0.5 +
        attendance_risk * 0.3 +
        completeness_risk * 0.2
    )
    return round(max(0.0, min(1.0, risk_score)), 4)


def _risk_level_from_score(score: float) -> RiskLevel:
    if score >= 0.7:
        return RiskLevel.HIGH
    if score >= 0.4:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


@router.get("/", response_model=List[RiskPredictionSchema])
def read_risk_predictions(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    query = db.query(RiskPrediction).filter(RiskPrediction.is_active == True)  # noqa: E712

    if student_id is not None:
        query = query.filter(RiskPrediction.student_id == student_id)
    if class_id is not None:
        query = query.filter(RiskPrediction.class_id == class_id)

    rows = query.order_by(RiskPrediction.prediction_date.desc()).offset(skip).limit(limit).all()

    if current_user.role == "admin":
        return rows

    # Teacher: filter only predictions belonging to teacher-owned classes
    class_ids = {r.class_id for r in rows}
    if not class_ids:
        return []
    teacher_classes = db.query(Class.id).filter(
        Class.id.in_(class_ids),
        Class.teacher_id == current_user.id
    ).all()
    allowed_class_ids = {c[0] for c in teacher_classes}
    return [r for r in rows if r.class_id in allowed_class_ids]


@router.get("/student/{student_id}/class/{class_id}/trend", response_model=List[RiskPredictionSchema])
def read_risk_prediction_trend(
    student_id: int,
    class_id: int,
    limit: int = Query(20, ge=1, le=200),
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

    rows = db.query(RiskPrediction).filter(
        RiskPrediction.student_id == student_id,
        RiskPrediction.class_id == class_id,
        RiskPrediction.is_active == True,  # noqa: E712
    ).order_by(RiskPrediction.prediction_date.asc()).limit(limit).all()

    return rows


@router.get("/{prediction_id}", response_model=RiskPredictionSchema)
def read_risk_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    record = db.query(RiskPrediction).filter(RiskPrediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Risk prediction not found")

    class_obj = db.query(Class).filter(Class.id == record.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_class_access(class_obj, current_user)

    return record


@router.post("/generate", response_model=RiskPredictionSchema, status_code=status.HTTP_201_CREATED)
def generate_risk_prediction(
    student_id: int,
    class_id: int,
    period: Optional[GradingPeriod] = None,
    persist: bool = True,
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
    _ensure_active_enrollment(db, student_id, class_id)

    features = _compute_risk_features(db, student_id, class_id, period)
    score = _score_from_features(features)
    level = _risk_level_from_score(score)

    row = RiskPrediction(
        student_id=student_id,
        class_id=class_id,
        prediction_date=datetime.now(timezone.utc),
        risk_score=score,
        risk_level=level,
        features_used=_safe_json_dumps(features),
        model_version=RISK_MODEL_VERSION,
        is_active=True,
    )

    if persist:
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    # Non-persistent preview
    return row


@router.post("/", response_model=RiskPredictionSchema, status_code=status.HTTP_201_CREATED)
def create_risk_prediction(
    prediction_in: RiskPredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    student = db.query(Student).filter(Student.id == prediction_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_obj = db.query(Class).filter(Class.id == prediction_in.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    _authorize_class_access(class_obj, current_user)
    _ensure_active_enrollment(db, prediction_in.student_id, prediction_in.class_id)

    payload = prediction_in.dict()
    if payload.get("features_used"):
        payload["features_used"] = _safe_json_dumps(_safe_json_loads(payload["features_used"]))

    if not payload.get("model_version"):
        payload["model_version"] = RISK_MODEL_VERSION

    record = RiskPrediction(**payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{prediction_id}", response_model=RiskPredictionSchema)
def update_risk_prediction(
    prediction_id: int,
    prediction_in: RiskPredictionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    record = db.query(RiskPrediction).filter(RiskPrediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Risk prediction not found")

    class_obj = db.query(Class).filter(Class.id == record.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_class_access(class_obj, current_user)

    update_data = prediction_in.dict(exclude_unset=True)

    if "features_used" in update_data and update_data["features_used"] is not None:
        update_data["features_used"] = _safe_json_dumps(_safe_json_loads(update_data["features_used"]))

    for field, value in update_data.items():
        setattr(record, field, value)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    record = db.query(RiskPrediction).filter(RiskPrediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Risk prediction not found")

    class_obj = db.query(Class).filter(Class.id == record.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_class_access(class_obj, current_user)

    record.is_active = False
    db.add(record)
    db.commit()
    return None
