from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.grade_transmutation import GradeTransmutation
from app.models.user import User
from app.schemas.grade_transmutation import (
    GradeTransmutation as GradeTransmutationSchema,
    GradeTransmutationCreate,
    GradeTransmutationUpdate,
    GradeTransmutationConversion,
)
from app.core import security

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _find_overlap(
    db: Session,
    raw_grade_min: float,
    raw_grade_max: float,
    exclude_id: int | None = None,
):
    query = db.query(GradeTransmutation).filter(
        GradeTransmutation.raw_grade_min < raw_grade_max,
        GradeTransmutation.raw_grade_max > raw_grade_min,
    )
    if exclude_id is not None:
        query = query.filter(GradeTransmutation.id != exclude_id)
    return query.first()


def _fallback_transmuted(raw_grade: float) -> float:
    return min(5.0, max(1.0, raw_grade / 20))


@router.get("/", response_model=List[GradeTransmutationSchema])
def list_transmutations(
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    return db.query(GradeTransmutation).order_by(GradeTransmutation.raw_grade_min.asc()).all()


@router.get("/convert", response_model=GradeTransmutationConversion)
def convert_raw_grade(
    raw_grade: float = Query(..., ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    row = db.query(GradeTransmutation).filter(
        GradeTransmutation.raw_grade_min <= raw_grade,
        GradeTransmutation.raw_grade_max > raw_grade
    ).order_by(GradeTransmutation.raw_grade_min.desc()).first()

    if not row and raw_grade == 100:
        row = db.query(GradeTransmutation).filter(
            GradeTransmutation.raw_grade_max == 100
        ).order_by(GradeTransmutation.raw_grade_min.desc()).first()

    if row:
        return GradeTransmutationConversion(
            raw_grade=raw_grade,
            transmuted_grade=float(row.transmuted_grade),
            raw_grade_min=float(row.raw_grade_min),
            raw_grade_max=float(row.raw_grade_max),
            description=row.description,
        )

    return GradeTransmutationConversion(
        raw_grade=raw_grade,
        transmuted_grade=_fallback_transmuted(raw_grade),
        raw_grade_min=None,
        raw_grade_max=None,
        description="Fallback conversion (no matching transmutation range found)",
    )


@router.post("/", response_model=GradeTransmutationSchema, status_code=status.HTTP_201_CREATED)
def create_transmutation(
    payload: GradeTransmutationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin),
):
    if payload.raw_grade_min >= payload.raw_grade_max:
        raise HTTPException(status_code=400, detail="raw_grade_min must be less than raw_grade_max")

    overlap = _find_overlap(db, payload.raw_grade_min, payload.raw_grade_max)
    if overlap:
        raise HTTPException(
            status_code=409,
            detail="Transmutation range overlaps with an existing range"
        )

    existing = db.query(GradeTransmutation).filter(
        GradeTransmutation.raw_grade_min == payload.raw_grade_min,
        GradeTransmutation.raw_grade_max == payload.raw_grade_max,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Transmutation range already exists")

    row = GradeTransmutation(**payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{transmutation_id}", response_model=GradeTransmutationSchema)
def update_transmutation(
    transmutation_id: int,
    payload: GradeTransmutationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin),
):
    row = db.query(GradeTransmutation).filter(GradeTransmutation.id == transmutation_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Grade transmutation not found")

    data = payload.dict(exclude_unset=True)

    new_min = data.get("raw_grade_min", row.raw_grade_min)
    new_max = data.get("raw_grade_max", row.raw_grade_max)
    if new_min >= new_max:
        raise HTTPException(status_code=400, detail="raw_grade_min must be less than raw_grade_max")

    overlap = _find_overlap(db, new_min, new_max, exclude_id=transmutation_id)
    if overlap:
        raise HTTPException(
            status_code=409,
            detail="Transmutation range overlaps with an existing range"
        )

    for k, v in data.items():
        setattr(row, k, v)

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{transmutation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transmutation(
    transmutation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin),
):
    row = db.query(GradeTransmutation).filter(GradeTransmutation.id == transmutation_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Grade transmutation not found")

    db.delete(row)
    db.commit()
    return {"ok": True}
