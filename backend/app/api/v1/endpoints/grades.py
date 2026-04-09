from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.grade import Grade, GradeComponent, GradingPeriod
from app.models.student import Student
from app.models.class_model import Class
from app.models.grade_weight import GradeWeight
from app.models.grade_transmutation import GradeTransmutation
from app.models.enrollment import Enrollment
from app.schemas.grade import (
    GradeCreate,
    Grade as GradeSchema,
    GradeUpdate,
    GradeCalculation,
    ClassPeriodGradeSummary,
    ClassPeriodGradeSummaryItem,
)
from app.core import security
from app.models.user import User
from datetime import date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_grade_weights(class_id: int, period: str, db: Session):
    weights = db.query(GradeWeight).filter(
        GradeWeight.class_id == class_id,
        GradeWeight.period == period
    ).first()

    if not weights:
        weights = GradeWeight(
            class_id=class_id,
            period=period,
            quizzes_weight=0.20,
            oral_participation_weight=0.10,
            graded_activity_weight=0.20,
            attendance_weight=0.10,
            major_exam_weight=0.40
        )
    return weights

def get_component_weight(weights: GradeWeight, component: GradeComponent) -> float:
    mapping = {
        GradeComponent.QUIZZES: weights.quizzes_weight,
        GradeComponent.ORAL_PARTICIPATION: weights.oral_participation_weight,
        GradeComponent.GRADED_ACTIVITY: weights.graded_activity_weight,
        GradeComponent.ATTENDANCE: weights.attendance_weight,
        GradeComponent.MAJOR_EXAM: weights.major_exam_weight,
    }
    return float(mapping.get(component, 0.0))

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
    raise HTTPException(status_code=403, detail="Not allowed to manage grades for this class")

def _validate_active_enrollment(db: Session, student: Student, class_obj: Class):
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.class_id == class_obj.id,
        Enrollment.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student is not actively enrolled in this class")

def _validate_score_constraints(score: float, max_score: float):
    if max_score <= 0:
        raise HTTPException(status_code=400, detail="max_score must be greater than 0")
    if score < 0:
        raise HTTPException(status_code=400, detail="score cannot be negative")
    if score > max_score:
        raise HTTPException(status_code=400, detail="score cannot be greater than max_score")

@router.get("/", response_model=List[GradeSchema])
def read_grades(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    component: Optional[GradeComponent] = None,
    period: Optional[GradingPeriod] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    query = db.query(Grade)

    if current_user.role == "teacher":
        query = query.join(Class, Class.id == Grade.class_id).filter(Class.teacher_id == current_user.id)

    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if class_id:
        query = query.filter(Grade.class_id == class_id)
    if component:
        query = query.filter(Grade.component == component)
    if period:
        query = query.filter(Grade.period == period)

    grades = query.offset(skip).limit(limit).all()
    return grades

# Keep static routes before dynamic /{grade_id}
@router.get("/student/{student_id}/class/{class_id}", response_model=List[GradeSchema])
def get_student_grades_by_class(
    student_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    grades = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.class_id == class_id
    ).all()

    return grades

@router.get("/calculate/{student_id}/{class_id}/{period}", response_model=GradeCalculation)
def calculate_final_grade_by_path(
    student_id: int,
    class_id: int,
    period: GradingPeriod,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    return _calculate_final_grade_logic(student_id, class_id, period, db, current_user)

@router.post("/calculate", response_model=GradeCalculation)
def calculate_final_grade(
    student_id: int,
    class_id: int,
    period: GradingPeriod,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    return _calculate_final_grade_logic(student_id, class_id, period, db, current_user)

@router.get("/summary/class-period", response_model=ClassPeriodGradeSummary)
def get_class_period_grade_summary(
    class_id: Optional[int] = None,
    class_code: Optional[str] = None,
    period: GradingPeriod = GradingPeriod.PRELIM,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin),
):
    class_obj = _resolve_class(db, class_id, class_code)
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_obj.id,
        Enrollment.is_active == True
    ).all()

    results: List[ClassPeriodGradeSummaryItem] = []
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        if not student or not student.is_active:
            continue

        calc = _calculate_final_grade_logic(student.id, class_obj.id, period, db, current_user)
        results.append(
            ClassPeriodGradeSummaryItem(
                student_id=student.id,
                student_code=student.student_id,
                student_name=f"{student.first_name} {student.last_name}",
                raw_grade=calc.raw_grade,
                transmuted_grade=calc.transmuted_grade,
            )
        )

    return ClassPeriodGradeSummary(
        class_id=class_obj.id,
        class_code=class_obj.class_code,
        period=period,
        total_students=len(results),
        results=results,
    )

@router.get("/{grade_id}", response_model=GradeSchema)
def read_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")

    class_obj = db.query(Class).filter(Class.id == grade.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    return grade

@router.post("/", response_model=GradeSchema)
def create_grade(
    grade_in: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = _resolve_student(db, grade_in.student_id, grade_in.student_code)
    class_obj = _resolve_class(db, grade_in.class_id, grade_in.class_code)
    _authorize_teacher_or_admin_for_class(current_user, class_obj)
    _validate_active_enrollment(db, student, class_obj)

    max_score = grade_in.max_score if grade_in.max_score is not None else 100.0
    _validate_score_constraints(grade_in.score, max_score)

    existing = db.query(Grade).filter(
        Grade.student_id == student.id,
        Grade.class_id == class_obj.id,
        Grade.component == grade_in.component,
        Grade.period == grade_in.period
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Grade already exists for this student/class/component/period"
        )

    grade_data = {
        "student_id": student.id,
        "class_id": class_obj.id,
        "component": grade_in.component,
        "period": grade_in.period,
        "score": grade_in.score,
        "max_score": max_score,
        "weight_percentage": grade_in.weight_percentage,
    }

    if grade_data.get("weight_percentage") is None:
        weights = get_grade_weights(class_obj.id, grade_in.period.value, db)
        grade_data["weight_percentage"] = get_component_weight(weights, grade_in.component)

    grade = Grade(**grade_data)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

@router.put("/{grade_id}", response_model=GradeSchema)
def update_grade(
    grade_id: int,
    grade_in: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")

    update_data = grade_in.dict(exclude_unset=True)

    student = _resolve_student(
        db,
        update_data.get("student_id", grade.student_id),
        update_data.get("student_code", None),
    )
    class_obj = _resolve_class(
        db,
        update_data.get("class_id", grade.class_id),
        update_data.get("class_code", None),
    )
    _authorize_teacher_or_admin_for_class(current_user, class_obj)
    _validate_active_enrollment(db, student, class_obj)

    new_component = update_data.get("component", grade.component)
    new_period = update_data.get("period", grade.period)
    new_score = update_data.get("score", grade.score)
    new_max_score = update_data.get("max_score", grade.max_score)
    _validate_score_constraints(new_score, new_max_score)

    duplicate = db.query(Grade).filter(
        Grade.student_id == student.id,
        Grade.class_id == class_obj.id,
        Grade.component == new_component,
        Grade.period == new_period,
        Grade.id != grade_id
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Grade already exists for this student/class/component/period"
        )

    grade.student_id = student.id
    grade.class_id = class_obj.id
    grade.component = new_component
    grade.period = new_period
    grade.score = new_score
    grade.max_score = new_max_score

    if "weight_percentage" in update_data:
        grade.weight_percentage = update_data["weight_percentage"]
    elif grade.weight_percentage is None:
        weights = get_grade_weights(class_obj.id, grade.period.value, db)
        grade.weight_percentage = get_component_weight(weights, grade.component)

    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")

    class_obj = db.query(Class).filter(Class.id == grade.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)

    db.delete(grade)
    db.commit()
    return {"ok": True}

def get_transmuted_grade(raw_grade: float, db: Session) -> float:
    row = db.query(GradeTransmutation).filter(
        GradeTransmutation.raw_grade_min <= raw_grade,
        GradeTransmutation.raw_grade_max > raw_grade
    ).order_by(GradeTransmutation.raw_grade_min.desc()).first()

    if not row and raw_grade == 100:
        row = db.query(GradeTransmutation).filter(
            GradeTransmutation.raw_grade_max == 100
        ).order_by(GradeTransmutation.raw_grade_min.desc()).first()

    if row:
        return float(row.transmuted_grade)

    return min(5.0, max(1.0, raw_grade / 20))

def _calculate_final_grade_logic(
    student_id: int,
    class_id: int,
    period: GradingPeriod,
    db: Session,
    current_user: User,
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    _authorize_teacher_or_admin_for_class(current_user, class_obj)
    _validate_active_enrollment(db, student, class_obj)

    weights = get_grade_weights(class_id, period.value, db)

    grades = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.class_id == class_id,
        Grade.period == period
    ).all()

    total_weighted_score = 0.0
    total_weight = 0.0

    grade_components = {
        GradeComponent.QUIZZES: {"score": 0.0, "weight": weights.quizzes_weight},
        GradeComponent.ORAL_PARTICIPATION: {"score": 0.0, "weight": weights.oral_participation_weight},
        GradeComponent.GRADED_ACTIVITY: {"score": 0.0, "weight": weights.graded_activity_weight},
        GradeComponent.ATTENDANCE: {"score": 0.0, "weight": weights.attendance_weight},
        GradeComponent.MAJOR_EXAM: {"score": 0.0, "weight": weights.major_exam_weight}
    }

    for grade in grades:
        if grade.component in grade_components:
            normalized_score = (grade.score / grade.max_score) * 100 if grade.max_score else 0.0
            grade_components[grade.component]["score"] = normalized_score

    for _, data in grade_components.items():
        if data["weight"] > 0:
            total_weighted_score += data["score"] * data["weight"]
            total_weight += data["weight"]

    final_grade = total_weighted_score / total_weight if total_weight > 0 else 0.0
    transmuted_grade = get_transmuted_grade(final_grade, db)

    return GradeCalculation(
        student_id=student_id,
        class_id=class_id,
        period=period,
        raw_grade=final_grade,
        transmuted_grade=transmuted_grade,
        component_breakdown=grade_components
    )
