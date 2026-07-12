import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.models.user import User

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class GenerateRequest(BaseModel):
    farm_id: str
    prediction_id: str


def _build_prompt(farm: Farm, prediction: Prediction) -> str:
    weather = json.loads(prediction.weather_summary) if prediction.weather_summary else {}
    bee_species = json.loads(prediction.bee_species) if prediction.bee_species else []
    return f"""You are an expert agronomist advising Indian farmers.

Farm Details:
- Crop: {farm.crop_type}
- Location: {farm.location_lat}, {farm.location_lng}

Current Conditions:
- Temperature: {weather.get('temperature', 'N/A')} C
- Humidity: {weather.get('humidity', 'N/A')}%
- Rainfall: {weather.get('rainfall', 'N/A')}mm
- Wind: {weather.get('wind_speed', 'N/A')}km/h

Predictions:
- Flowering Window: {prediction.flowering_start} to {prediction.flowering_end}
- Pollination Suitability Index: {prediction.psi_score}/100
- Risk Level: {prediction.risk_level}
- Nearby Bee Species: {', '.join(bee_species) if bee_species else 'N/A'}

Write a concise, actionable recommendation (max 200 words) in markdown format with:
1. A brief assessment
2. 2-3 specific actions the farmer should take
3. Any warnings if risk is Medium or High
4. End with a confidence statement

Be practical. Mention the crop by name."""


def _extract_gemini_text(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts") or []
    return "\n".join(part.get("text", "") for part in parts).strip()


async def _generate_gemini_recommendation(farm: Farm, prediction: Prediction) -> str:
    prompt = _build_prompt(farm, prediction)
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.llm_model or settings.gemini_model}:generateContent"
    )
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            url,
            params={"key": settings.llm_api_key or settings.gemini_api_key},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 300,
                },
            },
        )
        response.raise_for_status()
    recommendation = _extract_gemini_text(response.json())
    if not recommendation:
        raise ValueError("Gemini returned an empty recommendation")
    return recommendation


def _generate_local_recommendation(farm: Farm, prediction: Prediction) -> str:
    risk_advisory = ""
    if prediction.risk_level == "High":
        risk_advisory = (
            f"\n\n**Warning:** The PSI of {prediction.psi_score}/100 indicates "
            "High risk. Consider delaying sowing or using supplemental pollination methods. "
            "Monitor weather conditions closely."
        )
    elif prediction.risk_level == "Medium":
        risk_advisory = (
            f"\n\n**Caution:** The PSI of {prediction.psi_score}/100 is moderate. "
            "Ensure adequate irrigation and consider introducing managed pollinators."
        )
    else:
        risk_advisory = (
            f"\n\nConditions are favourable. Maintain regular crop management practices."
        )

    return (
        f"## Assessment for {farm.crop_type}\n\n"
        f"Based on current conditions (temp {prediction.psi_score}°C, "
        f"rainfall in normal range) and the predicted flowering window "
        f"({prediction.flowering_start} to {prediction.flowering_end}), "
        f"the pollination suitability is **{prediction.risk_level.lower()} risk** "
        f"with a score of **{prediction.psi_score}/100**."
        f"{risk_advisory}\n\n"
        f"**Confidence:** Moderate — predictions are based on seasonal models and "
        f"local weather data. Real-time satellite data will improve accuracy."
    )


@router.post("/generate", response_model=dict)
async def generate_recommendation(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    farm = db.scalar(select(Farm).where(Farm.id == payload.farm_id, Farm.user_id == current_user.id))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    prediction = db.scalar(
        select(Prediction).where(
            Prediction.id == payload.prediction_id,
            Prediction.farm_id == farm.id,
        )
    )
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    active_llm_key = settings.llm_api_key or settings.gemini_api_key
    if active_llm_key and active_llm_key != "change-me-in-production":
        try:
            recommendation = await _generate_gemini_recommendation(farm, prediction)
        except (httpx.HTTPError, ValueError):
            recommendation = _generate_local_recommendation(farm, prediction)
    else:
        recommendation = _generate_local_recommendation(farm, prediction)

    prediction.recommendation = recommendation
    db.commit()

    return {"recommendation": recommendation}
