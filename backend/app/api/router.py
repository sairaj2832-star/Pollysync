from fastapi import APIRouter

from app.agent.router import router as agent_router
from app.api.routes import (
    auth,
    farms,
    health,
    maps,
    notification_preferences,
    notifications,
    predictions,
    recommendations,
    team,
    weather,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(farms.router)
api_router.include_router(notifications.router)
api_router.include_router(notification_preferences.router)
api_router.include_router(weather.router)
api_router.include_router(predictions.router)
api_router.include_router(recommendations.router)
api_router.include_router(maps.router)
api_router.include_router(team.router)
api_router.include_router(agent_router)
