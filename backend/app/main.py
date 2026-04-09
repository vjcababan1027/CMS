from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.tasks.notification_scheduler import start_notification_scheduler, stop_notification_scheduler

app = FastAPI(
    title="Intelligent Decision Support System",
    description="A comprehensive system for school performance enhancement",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    start_notification_scheduler()

@app.on_event("shutdown")
async def on_shutdown():
    stop_notification_scheduler()

@app.get("/")
async def root():
    return {"message": "Welcome to the Intelligent Decision Support System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
