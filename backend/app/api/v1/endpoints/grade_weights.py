from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.grade_weight import GradeWeight
from app.schemas.grade_weight import GradeWeightCreate, GradeWeight as GradeWeightSchema, GradeWeightUpdate
from app.core import security
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[GradeWeightSchema])
def read_grade_weights(
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[int] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    query = db.query(GradeWeight)

    if class_id:
        query = query.filter(GradeWeight.class_id == class_id)
    if period:
        query = query.filter(GradeWeight.period == period)

    grade_weights = query.offset(skip).limit(limit).all()
    return grade_weights

@router.get("/{weight_id}", response_model=GradeWeightSchema)
def read_grade_weight(
    weight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade_weight = db.query(GradeWeight).filter(GradeWeight.id == weight_id).first()
    if grade_weight is None:
        raise HTTPException(status_code=404, detail="Grade weight not found")
    return grade_weight

@router.post("/", response_model=GradeWeightSchema)
def create_grade_weight(
    weight_in: GradeWeightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    # Check if weight already exists for this class/period
    weight = db.query(GradeWeight).filter(
        GradeWeight.class_id == weight_in.class_id,
        GradeWeight.period == weight_in.period
    ).first()

    if weight:
        raise HTTPException(
            status_code=409,
            detail="Grade weight already exists for this class and period"
        )

    # Validate that weights sum to 100%
    total_weight = (
        weight_in.quizzes_weight +
        weight_in.oral_participation_weight +
        weight_in.graded_activity_weight +
        weight_in.attendance_weight +
        weight_in.major_exam_weight
    )

    if abs(total_weight - 1.0) > 0.01:  # Allow small floating point differences
        raise HTTPException(
            status_code=400,
            detail="Grade weights must sum to 1.0 (100%)"
        )

    grade_weight = GradeWeight(**weight_in.dict())
    db.add(grade_weight)
    db.commit()
    db.refresh(grade_weight)
    return grade_weight

@router.put("/{weight_id}", response_model=GradeWeightSchema)
def update_grade_weight(
    weight_id: int,
    weight_in: GradeWeightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade_weight = db.query(GradeWeight).filter(GradeWeight.id == weight_id).first()
    if grade_weight is None:
        raise HTTPException(status_code=404, detail="Grade weight not found")

    update_data = weight_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade_weight, field, value)

    # Validate that weights sum to 100% if any weight fields were updated
    weight_fields = ['quizzes_weight', 'oral_participation_weight', 'graded_activity_weight', 'attendance_weight', 'major_exam_weight']
    if any(field in update_data for field in weight_fields):
        total_weight = (
            grade_weight.quizzes_weight +
            grade_weight.oral_participation_weight +
            grade_weight.graded_activity_weight +
            grade_weight.attendance_weight +
            grade_weight.major_exam_weight
        )

        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail="Grade weights must sum to 1.0 (100%)"
            )

    db.add(grade_weight)
    db.commit()
    db.refresh(grade_weight)
    return grade_weight

@router.delete("/{weight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade_weight(
    weight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade_weight = db.query(GradeWeight).filter(GradeWeight.id == weight_id).first()
    if grade_weight is None:
        raise HTTPException(status_code=404, detail="Grade weight not found")
    db.delete(grade_weight)
    db.commit()
    return {"ok": True}