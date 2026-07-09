from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient, email: str = "farm-user@example.com") -> dict[str, str]:
    password = "StrongPass1!"
    payload = {
        "email": email,
        "password": password,
        "full_name": "Farm User",
    }
    registered = client.post("/api/auth/register", json=payload)
    assert registered.status_code in {201, 409}
    logged_in = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert logged_in.status_code == 200
    token = logged_in.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
        "crop": "Mustard",
        "location": "Nashik, Maharashtra",
        "area_acres": 5.5,
        "soil_type": "loamy",
    }

    with TestClient(app) as client:
        headers = _auth_headers(client)
        created = client.post("/api/farms", json=payload, headers=headers)
        farms = client.get("/api/farms", headers=headers)

    assert created.status_code == 201
    assert created.json()["crop_type"] == "Mustard"
    assert created.json()["crop"] == "Mustard"
    assert created.json()["location"] == "Nashik, Maharashtra"
    assert created.json()["area_acres"] == 5.5
    assert farms.status_code == 200
    assert any(farm["name"] == "Demo Farm" for farm in farms.json())


def test_mark_notification_read() -> None:
    payload = {
        "name": "Alerts Farm",
        "crop": "Sunflower",
        "location": "Pune, Maharashtra",
        "area_acres": 3.0,
        "soil_type": "sandy",
    }

    with TestClient(app) as client:
        headers = _auth_headers(client, email="notify-user@example.com")
        created = client.post("/api/farms", json=payload, headers=headers)
        assert created.status_code == 201

        notifications = client.get("/api/notifications", headers=headers)
        assert notifications.status_code == 200
        assert len(notifications.json()) >= 1

        notification_id = notifications.json()[0]["id"]
        updated = client.patch(f"/api/notifications/{notification_id}/read", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["read"] is True


def test_auth_register_login_refresh_and_logout() -> None:
    email = "api-user@example.com"
    password = "StrongPass1!"
    register_payload = {
        "email": email,
        "password": password,
        "full_name": "API User",
    }

    with TestClient(app) as client:
        registered = client.post("/api/auth/register", json=register_payload)

        assert registered.status_code in {201, 409}
        if registered.status_code == 201:
            registered_body = registered.json()
            assert registered_body["token_type"] == "bearer"
            assert registered_body["user"]["email"] == email

        logged_in = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert logged_in.status_code == 200
        login_body = logged_in.json()
        access_token = login_body["access_token"]
        refresh_token = login_body["refresh_token"]

        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert me.status_code == 200
        assert me.json()["email"] == email

        oauth2_token = client.post(
            "/api/auth/token",
            data={"username": email, "password": password},
        )
        assert oauth2_token.status_code == 200
        assert oauth2_token.json()["token_type"] == "bearer"

        refreshed = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert refreshed.status_code == 200
        assert refreshed.json()["refresh_token"] != refresh_token

        logged_out = client.post(
            "/api/auth/logout",
            json={"refresh_token": refreshed.json()["refresh_token"]},
        )
        assert logged_out.status_code == 204


def test_current_weather_uses_farm_coordinates(monkeypatch) -> None:
    calls = []

    async def fake_fetch_weather(lat: float, lng: float) -> dict:
        calls.append((lat, lng))
        return {
            "current": {
                "temperature_2m": 27,
                "relative_humidity_2m": 66,
                "precipitation": 1.2,
                "wind_speed_10m": 7.5,
            }
        }

    monkeypatch.setattr("app.api.routes.weather.fetch_weather", fake_fetch_weather)

    payload = {
        "name": "Weather Farm Unique",
        "crop_type": "Mustard",
        "location_lat": 19.9975,
        "location_lng": 73.7898,
    }

    with TestClient(app) as client:
        farm = client.post("/api/farms", json=payload).json()
        response = client.get("/api/weather/current", params={"farm_id": farm["id"]})

    assert response.status_code == 200
    assert calls == [(payload["location_lat"], payload["location_lng"])]
    assert response.json()["temperature"] == 27


def test_prediction_creates_recommendation_and_dashboard_alias(monkeypatch) -> None:
    async def fake_fetch_weather(lat: float, lng: float) -> dict:
        return {
            "current": {
                "temperature_2m": 25,
                "relative_humidity_2m": 64,
                "precipitation": 0,
                "wind_speed_10m": 8,
            }
        }

    monkeypatch.setattr("app.services.prediction_service.fetch_weather", fake_fetch_weather)

    payload = {
        "name": "Prediction Farm Unique",
        "crop_type": "Mustard",
        "location_lat": 20.011,
        "location_lng": 73.79,
    }

    with TestClient(app) as client:
        farm = client.post("/api/farms", json=payload).json()
        prediction = client.post("/api/predictions", json={"farm_id": farm["id"]})
        dashboard = client.get("/api/dashboard/summary", params={"farm_id": farm["id"]})

    assert prediction.status_code == 201
    body = prediction.json()
    assert body["recommendation"]
    assert body["weather_summary"]["temperature"] == 25
    assert dashboard.status_code == 200
    assert dashboard.json()["latest_prediction"]["id"] == body["id"]
