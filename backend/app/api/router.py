from fastapi import APIRouter

from app.api.routes import farms, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(farms.router)
