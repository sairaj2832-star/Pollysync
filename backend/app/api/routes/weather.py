from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.weather_cache import WeatherCache
from app.schemas.weather import ForecastDay, WeatherCurrent, WeatherForecast
from app.services.weather_service import (
    fetch_weather,
    get_cached_weather,
    parse_forecast,
    cache_weather,
)

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=WeatherCurrent)
async def current_weather(farm_id: int = Query(...), db: Session = Depends(get_db)) -> WeatherCurrent:
    cached = get_cached_weather(farm_id, db)
    if cached:
        return WeatherCurrent(
            temperature=cached.temperature,
            humidity=cached.humidity,
            rainfall=cached.rainfall,
            wind_speed=cached.wind_speed,
            timestamp=cached.timestamp.isoformat() if cached.timestamp else None,
        )
    raw = await fetch_weather(0, 0)
    record = cache_weather(farm_id, raw, db)
    return WeatherCurrent(
        temperature=record.temperature,
        humidity=record.humidity,
        rainfall=record.rainfall,
        wind_speed=record.wind_speed,
        timestamp=record.timestamp.isoformat() if record.timestamp else None,
    )


@router.get("/forecast", response_model=WeatherForecast)
async def forecast(
    farm_id: int = Query(...),
    days: int = Query(7, ge=1, le=16),
    db: Session = Depends(get_db),
) -> WeatherForecast:
    from app.models.farm import Farm
    farm = db.get(Farm, farm_id)
    if not farm:
        return WeatherForecast(forecast=[])
    raw = await fetch_weather(farm.location_lat, farm.location_lng)
    forecast_data = parse_forecast(raw)[:days]
    return WeatherForecast(forecast=[ForecastDay(**d) for d in forecast_data])
