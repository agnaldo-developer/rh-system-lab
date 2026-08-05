from fastapi import FastAPI

from app.api.routes.departments import router as departments_router
from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
)


app.include_router(health_router)

app.include_router(
    departments_router,
    prefix="/api/v1",
)
