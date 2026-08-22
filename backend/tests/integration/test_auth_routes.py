from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_register_login_and_me(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "User@Example.com",
            "password": "strong-password",
            "username": "user",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"
    assert "password_hash" not in register_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"


def test_duplicate_email_is_rejected(client: TestClient) -> None:
    payload = {
        "email": "same@example.com",
        "password": "strong-password",
    }

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_wrong_password_is_rejected(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "strong-password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "bad-password",
        },
    )

    assert response.status_code == 401


def test_missing_malformed_and_expired_tokens_are_rejected(client: TestClient) -> None:
    missing_response = client.get("/api/v1/auth/me")
    malformed_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-token"},
    )

    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    expired_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert missing_response.status_code == 401
    assert malformed_response.status_code == 401
    assert expired_response.status_code == 401
