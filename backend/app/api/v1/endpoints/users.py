from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, User as UserSchema, UserUpdate
from app.core import security
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=UserSchema)
def read_current_user(
    current_user: User = Depends(security.get_current_active_user)
):
    return current_user

@router.get("/", response_model=List[UserSchema])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = security.get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    user.is_active = False
    db.add(user)
    db.commit()
    return {"ok": True}

@router.patch("/{user_id}/reactivate", response_model=UserSchema)
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
