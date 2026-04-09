from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, students, classes, attendance, grades, grade_weights, risk_predictions, parent_reporting, grade_transmutations, reports, interventions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
api_router.include_router(grade_weights.router, prefix="/grade-weights", tags=["grade-weights"])
api_router.include_router(risk_predictions.router, prefix="/risk-predictions", tags=["risk-predictions"])
api_router.include_router(parent_reporting.router, prefix="/parent-reporting", tags=["parent-reporting"])
api_router.include_router(grade_transmutations.router, prefix="/grade-transmutations", tags=["grade-transmutations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(interventions.router, prefix="/interventions", tags=["interventions"])
