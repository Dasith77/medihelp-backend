from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.sessions import router as sessions_router
from app.routers.slots import router as slots_router
from app.routers.bookings import router as bookings_router
from app.routers.queue import router as queue_router
from app.routers.notifications import router as notifications_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "doctors_router",
    "sessions_router",
    "slots_router",
    "bookings_router",
    "queue_router",
    "notifications_router",
    "dashboard_router",
]
