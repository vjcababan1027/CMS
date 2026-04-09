from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.models.student import Student
from app.models.class_model import Class
from app.schemas.student import StudentCreate, Student as StudentSchema, StudentUpdate
from app.core import security
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[StudentSchema])
def read_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentSchema)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/", response_model=StudentSchema)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    # Check if student_id already exists
    student = db.query(Student).filter(Student.student_id == student_in.student_id).first()
    if student:
        raise HTTPException(
            status_code=400,
            detail="Student with this ID already exists"
        )

    if student_in.class_code:
        class_obj = db.query(Class).filter(Class.class_code == student_in.class_code).first()
        if class_obj is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid class code. Class not found."
            )

    student = Student(**student_in.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.put("/{student_id}", response_model=StudentSchema)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student_in.dict(exclude_unset=True)

    if "student_id" in update_data:
        duplicate = db.query(Student).filter(
            Student.student_id == update_data["student_id"],
            Student.id != student_id
        ).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Student with this ID already exists")

    if "class_code" in update_data and update_data["class_code"]:
        class_obj = db.query(Class).filter(Class.class_code == update_data["class_code"]).first()
        if class_obj is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid class code. Class not found."
            )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_teacher_or_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"ok": True}