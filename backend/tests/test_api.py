from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "pollisync-api",
    }


def test_create_and_list_farm() -> None:
    payload = {
        "name": "Demo Farm",
        "crop_type": "Mustard",
        "location_lat": 20.011,
        "location_lng": 73.79,
    }

    with TestClient(app) as client:
        created = client.post("/api/farms", json=payload)
        farms = client.get("/api/farms")

    assert created.status_code == 201
    assert created.json()["crop_type"] == "Mustard"
    assert farms.status_code == 200
    assert any(farm["name"] == "Demo Farm" for farm in farms.json())
