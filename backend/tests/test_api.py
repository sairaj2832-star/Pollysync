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
