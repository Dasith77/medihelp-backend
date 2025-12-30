from fastapi import APIRouter

from app.api.endpoints import auth, bookings, doctors, sessions

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/admin/auth",
    tags=["Admin Authentication"],
)

api_router.include_router(
    doctors.router,
    prefix="/doctors",
    tags=["Doctors"],
)

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["Sessions"],
)

api_router.include_router(
    bookings.router,
    prefix="/bookings",
    tags=["Bookings"],
)
