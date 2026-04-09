from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.risk_prediction import RiskPrediction, RiskLevel
from app.schemas.risk_prediction import RiskPrediction as RiskPredictionSchema
from app.schemas.intervention import (
    InterventionRecommendation,
    InterventionPlanResponse,
)

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


def build_recommendations_structured(risk_level: str, risk_score: float) -> List[InterventionRecommendation]:
    recs: List[InterventionRecommendation] = []

    # Always include monitoring
    recs.append(
        InterventionRecommendation(
            category="monitoring",
            action="Track weekly grades and attendance with documented progress notes",
            priority=3,
            rationale="Continuous monitoring helps detect further decline early.",
        )
    )

    if risk_level == RiskLevel.HIGH.value or risk_score >= 0.8:
        recs.extend(
            [
                InterventionRecommendation(
                    category="parent_notification",
                    action="Notify parent/guardian immediately and schedule conference within 7 days",
                    priority=1,
                    rationale="High-risk learners require immediate family involvement.",
                ),
                InterventionRecommendation(
                    category="counseling",
                    action="Schedule counseling session and psychosocial check-in",
                    priority=1,
                    rationale="High risk may involve non-academic factors impacting performance.",
                ),
                InterventionRecommendation(
                    category="remedial",
                    action="Enroll student in remedial sessions for weak competencies",
                    priority=2,
                    rationale="Remediation targets foundational gaps causing low performance.",
                ),
                InterventionRecommendation(
                    category="extra_assignments",
                    action="Provide scaffolded extra assignments with strict weekly deadlines",
                    priority=2,
                    rationale="Structured practice improves mastery and accountability.",
                ),
            ]
        )
    elif risk_level == RiskLevel.MODERATE.value or risk_score >= 0.5:
        recs.extend(
            [
                InterventionRecommendation(
                    category="extra_assignments",
                    action="Assign targeted extra exercises for low-scoring competencies",
                    priority=2,
                    rationale="Moderate risk can be reduced through focused reinforcement.",
                ),
                InterventionRecommendation(
                    category="remedial",
                    action="Plan short remedial blocks during advisory or support hours",
                    priority=2,
                    rationale="Short-cycle remediation can prevent risk escalation.",
                ),
                InterventionRecommendation(
                    category="parent_notification",
                    action="Include parent update in bi-weekly progress communication",
                    priority=3,
                    rationale="Parent awareness supports consistency at home.",
                ),
            ]
        )
    else:
        recs.extend(
            [
                InterventionRecommendation(
                    category="extra_assignments",
                    action="Offer optional enrichment tasks to sustain momentum",
                    priority=4,
                    rationale="Low-risk learners benefit from continued challenge and engagement.",
                )
            ]
        )

    return recs


def build_recommendations(risk_level: str, risk_score: float) -> List[str]:
    """
    Backward-compatible plain-text recommendations.
    """
    structured = build_recommendations_structured(risk_level, risk_score)
    return [f"[{r.category}] {r.action}" for r in structured]


def _build_intervention_response(pred: RiskPrediction) -> InterventionPlanResponse:
    return InterventionPlanResponse(
        student_id=pred.student_id,
        class_id=pred.class_id,
        generated_at=datetime.now(timezone.utc),
        prediction=RiskPredictionSchema.model_validate(pred),
        recommendations=build_recommendations_structured(pred.risk_level.value, float(pred.risk_score)),
    )


@router.get("/risk-prediction/{prediction_id}", response_model=InterventionPlanResponse)
def get_intervention_by_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    pred = db.query(RiskPrediction).filter(RiskPrediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Risk prediction not found")

    class_obj = db.query(Class).filter(Class.id == pred.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_class_access(class_obj, current_user)

    return _build_intervention_response(pred)


@router.get("/student/{student_id}/class/{class_id}/latest", response_model=InterventionPlanResponse)
def get_latest_intervention(
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

    pred = db.query(RiskPrediction).filter(
        RiskPrediction.student_id == student_id,
        RiskPrediction.class_id == class_id,
        RiskPrediction.is_active == True  # noqa: E712
    ).order_by(RiskPrediction.prediction_date.desc()).first()

    if not pred:
        raise HTTPException(status_code=404, detail="No active risk prediction found")

    return _build_intervention_response(pred)


@router.get("/student/{student_id}/class/{class_id}", response_model=InterventionPlanResponse)
def get_intervention_by_student_class(
    student_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    """
    Returns intervention recommendations for the latest active prediction
    for a student within a class. Alias endpoint for integration simplicity.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    _authorize_class_access(class_obj, current_user)

    pred = db.query(RiskPrediction).filter(
        RiskPrediction.student_id == student_id,
        RiskPrediction.class_id == class_id,
        RiskPrediction.is_active == True  # noqa: E712
    ).order_by(RiskPrediction.prediction_date.desc()).first()

    if not pred:
        raise HTTPException(status_code=404, detail="No active risk prediction found")

    return _build_intervention_response(pred)
