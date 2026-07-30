from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth_router,
    doctors_router,
    sessions_router,
    slots_router,
    bookings_router,
    queue_router,
    notifications_router,
    dashboard_router,
)

app = FastAPI(
    title="MediHelp API",
    description="Medical Appointment Queue Booking System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(sessions_router)
app.include_router(slots_router)
app.include_router(bookings_router)
app.include_router(queue_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to MediHelp API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
