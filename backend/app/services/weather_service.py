from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.weather_cache import WeatherCache

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lng}"
    "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    "&timezone=auto"
)


async def fetch_weather(lat: float, lng: float) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_URL.format(lat=lat, lng=lng), timeout=10)
        resp.raise_for_status()
        return resp.json()


def get_fallback_weather(lat: float, lng: float) -> dict:
    # Conservative fallback so prediction flows can continue even if the
    # upstream weather API is unavailable locally.
    return {
        "current": {
            "temperature_2m": 28,
            "relative_humidity_2m": 62,
            "precipitation": 1.2,
            "wind_speed_10m": 9.5,
        },
        "daily": {
            "time": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "precipitation_sum": [],
        },
        "fallback": True,
        "source_location": {"lat": lat, "lng": lng},
    }


def get_cached_weather(farm_id: str, db: Session) -> WeatherCache | None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    return (
        db.query(WeatherCache)
        .filter(
            WeatherCache.farm_id == farm_id,
            WeatherCache.timestamp > cutoff,
        )
        .order_by(WeatherCache.timestamp.desc())
        .first()
    )


def cache_weather(farm_id: str, data: dict, db: Session) -> WeatherCache:
    current = data.get("current", {})
    record = WeatherCache(
        farm_id=farm_id,
        temperature=current.get("temperature_2m", 0),
        humidity=current.get("relative_humidity_2m", 0),
        rainfall=current.get("precipitation", 0),
        wind_speed=current.get("wind_speed_10m", 0),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def parse_forecast(raw: dict) -> list[dict]:
    daily = raw.get("daily", {})
    dates = daily.get("time", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_sum", [])
    return [
        {"date": d, "temp_max": t_max[i], "temp_min": t_min[i], "rainfall": rain[i]}
        for i, d in enumerate(dates)
    ]
