from fastapi import APIRouter

from app.api.routes import auth, farms, health, maps, notifications, predictions, recommendations, weather

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(farms.router)
api_router.include_router(notifications.router)
api_router.include_router(weather.router)
api_router.include_router(predictions.router)
api_router.include_router(recommendations.router)
api_router.include_router(maps.router)
api_router.include_router(dashboard.router)
