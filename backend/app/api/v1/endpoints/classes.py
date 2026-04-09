from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.models.class_model import Class
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.class_schema import (
    ClassCreate,
    Class as ClassSchema,
    ClassUpdate,
    ClassRosterResponse,
    EnrollmentActionResponse,
)
from app.core import security
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ClassSchema])
def read_classes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    classes = db.query(Class).offset(skip).limit(limit).all()
    return classes

@router.get("/by-id/{class_id}", response_model=ClassSchema)
def read_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

@router.post("/", response_model=ClassSchema)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    # Check teacher exists and has teacher role
    teacher = db.query(User).filter(User.id == class_in.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Assigned teacher user not found")
    if teacher.role != "teacher":
        raise HTTPException(status_code=400, detail="Assigned user must have teacher role")

    # Check if class_code already exists
    class_obj = db.query(Class).filter(Class.class_code == class_in.class_code).first()
    if class_obj:
        raise HTTPException(
            status_code=400,
            detail="Class with this code already exists"
        )
    class_obj = Class(**class_in.dict())
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj

@router.put("/{class_id}", response_model=ClassSchema)
def update_class(
    class_id: int,
    class_in: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")

    update_data = class_in.dict(exclude_unset=True)

    if "class_code" in update_data:
        duplicate = db.query(Class).filter(
            Class.class_code == update_data["class_code"],
            Class.id != class_id
        ).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Class with this code already exists")

    if "teacher_id" in update_data:
        teacher = db.query(User).filter(User.id == update_data["teacher_id"]).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Assigned teacher user not found")
        if teacher.role != "teacher":
            raise HTTPException(status_code=400, detail="Assigned user must have teacher role")

    for field, value in update_data.items():
        setattr(class_obj, field, value)

    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj

@router.get("/{class_code}/students", response_model=ClassRosterResponse)
def get_class_students_by_code(
    class_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.class_code == class_code).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")

    students = (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Enrollment.class_id == class_obj.id,
            Enrollment.is_active == True,
            Student.is_active == True,
        )
        .all()
    )

    return ClassRosterResponse(
        class_code=class_obj.class_code,
        class_name=class_obj.name,
        total_students=len(students),
        students=students,
    )

@router.post("/{class_code}/students/{student_id}", response_model=EnrollmentActionResponse)
def add_student_to_class_by_code(
    class_code: str,
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.class_code == class_code).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.class_id == class_obj.id, Enrollment.student_id == student.id)
        .first()
    )

    if enrollment and enrollment.is_active:
        raise HTTPException(status_code=400, detail="Student already enrolled in this class")

    if enrollment and not enrollment.is_active:
        enrollment.is_active = True
        db.add(enrollment)
    else:
        enrollment = Enrollment(class_id=class_obj.id, student_id=student.id, is_active=True)
        db.add(enrollment)

    student.class_code = class_obj.class_code
    db.add(student)
    db.commit()

    return EnrollmentActionResponse(
        message="Student enrolled successfully",
        class_code=class_obj.class_code,
        student_id=student.student_id,
        enrollment_active=True,
    )

@router.delete("/{class_code}/students/{student_id}", response_model=EnrollmentActionResponse)
def remove_student_from_class_by_code(
    class_code: str,
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.class_code == class_code).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.class_id == class_obj.id,
            Enrollment.student_id == student.id,
            Enrollment.is_active == True,
        )
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Active enrollment not found")

    enrollment.is_active = False
    db.add(enrollment)

    active_other_enrollment = (
        db.query(Enrollment)
        .join(Class, Class.id == Enrollment.class_id)
        .filter(
            Enrollment.student_id == student.id,
            Enrollment.is_active == True,
            Class.class_code == student.class_code,
        )
        .first()
    )
    if not active_other_enrollment and student.class_code == class_obj.class_code:
        student.class_code = None
        db.add(student)

    db.commit()

    return EnrollmentActionResponse(
        message="Student removed from class successfully",
        class_code=class_obj.class_code,
        student_id=student.student_id,
        enrollment_active=False,
    )

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(class_obj)
    db.commit()
    return {"ok": True}