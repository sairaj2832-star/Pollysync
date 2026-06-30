import json
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.models.prediction import Prediction

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class GenerateRequest(BaseModel):
    farm_id: int
    prediction_id: int


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
def generate_recommendation(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
) -> dict:
    farm = db.get(Farm, payload.farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    prediction = db.get(Prediction, payload.prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    api_key = os.getenv("OPENAI_API_KEY") or ""
    if api_key and api_key != "change-me-in-production":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = _build_prompt(farm, prediction)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful agronomist."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            recommendation = response.choices[0].message.content
        except Exception:
            recommendation = _generate_local_recommendation(farm, prediction)
    else:
        recommendation = _generate_local_recommendation(farm, prediction)

    prediction.recommendation = recommendation
    db.commit()

    return {"recommendation": recommendation}
