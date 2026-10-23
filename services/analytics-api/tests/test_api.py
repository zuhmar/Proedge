"""Integration tests use the migrated PostgreSQL database with isolated test users."""

import uuid

import pytest
from app.db import SessionLocal
from app.main import app, requests
from app.models import (
    PasswordReset,
    Session,
    User,
    UserPreference,
    Watchlist,
    WatchlistItem,
)
from fastapi.testclient import TestClient
from sqlalchemy import delete, select


@pytest.fixture
def client():
    requests.clear()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def account(client):
    email = f"test-{uuid.uuid4().hex}@example.com"
    credentials = {"email": email, "password": "a-secure-test-password-2026"}
    r = client.post("/api/v1/auth/register", json=credentials)
    assert r.status_code == 201
    data = r.json()
    client.headers["x-csrf-token"] = data["csrf_token"]
    yield data, credentials
    with SessionLocal.begin() as db:
        uid = data["user"]["id"]
        ids = select(Watchlist.id).where(Watchlist.user_id == uid)
        db.execute(delete(WatchlistItem).where(WatchlistItem.watchlist_id.in_(ids)))
        db.execute(delete(Watchlist).where(Watchlist.user_id == uid))
        db.execute(delete(UserPreference).where(UserPreference.user_id == uid))
        db.execute(delete(Session).where(Session.user_id == uid))
        db.execute(delete(PasswordReset).where(PasswordReset.user_id == uid))
        db.execute(delete(User).where(User.id == uid))


def test_database_health(client):
    assert client.get("/api/v1/health").json()["database"] == "ok"


def test_demo_schedule_and_filters(client):
    response = client.get("/api/v1/games?selected_date=2026-10-23&sport=NBA")
    assert response.status_code == 200
    games = response.json()["items"]
    assert len(games) == 2
    assert all(
        g["demo"] and g["prediction"] is None and g["sport"] == "NBA" for g in games
    )
    assert client.get("/api/v1/games?selected_date=2026-10-24").json()["items"] == []
    assert client.get("/api/v1/games?limit=101").status_code == 422
    assert client.get("/api/v1/games?sport=MLB").status_code == 422
    assert (
        client.get("/api/v1/games?limit=1&offset=1").json()["items"][0]["id"]
        != games[0]["id"]
    )


def test_auth_lifecycle_and_csrf(client, account):
    data, credentials = account
    assert client.get("/api/v1/auth/me").json()["user"]["email"] == credentials["email"]
    cookie = client.cookies.get("proedge_session")
    assert cookie
    with SessionLocal() as db:
        user = db.get(User, data["user"]["id"])
        assert user.password_hash != credentials["password"]
        assert (
            db.scalar(select(Session).where(Session.user_id == user.id)).token_hash
            != cookie
        )
    assert (
        client.post(
            "/api/v1/auth/logout", headers={"x-csrf-token": "wrong"}
        ).status_code
        == 403
    )
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login", json={**credentials, "password": "incorrect-password"}
        ).status_code
        == 401
    )
    response = client.post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 200
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()


def test_private_watchlist_and_duplicates(client, account):
    w = client.post("/api/v1/watchlists", json={"name": "Research"}).json()
    game_id = client.get("/api/v1/games").json()["items"][0]["id"]
    for _ in range(2):
        assert (
            client.post(
                f"/api/v1/watchlists/{w['id']}/items", json={"game_id": game_id}
            ).status_code
            == 201
        )
    assert len(client.get("/api/v1/watchlists").json()[0]["games"]) == 1
    other = TestClient(app)
    assert other.get("/api/v1/watchlists").status_code == 401
    assert (
        client.post(
            "/api/v1/watchlists/999999/items", json={"game_id": game_id}
        ).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/watchlists/{w['id']}/items/{game_id}").status_code
        == 204
    )
    assert client.get("/api/v1/watchlists").json()[0]["games"] == []


def test_preferences_and_role(client, account):
    preferences = {"sport": "NFL", "timezone": "UTC", "odds_format": "decimal"}
    assert client.put("/api/v1/settings", json=preferences).json() == preferences
    assert client.get("/api/v1/settings").json() == preferences
    assert (
        client.put(
            "/api/v1/settings", json={**preferences, "timezone": "Fake/Zone"}
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/api/v1/settings", json={**preferences, "timezone": "../UTC"}
        ).status_code
        == 422
    )
    assert client.get("/api/v1/admin/health").status_code == 403


def test_security_and_unavailable_features(client):
    assert (
        client.post(
            "/api/v1/auth/login",
            headers={"origin": "https://attacker.example"},
            json={},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": "bad", "password": "short"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/auth/password-reset", json={"email": "missing@example.com"}
        ).status_code
        == 202
    )
    status = client.get("/api/v1/data/status").json()
    assert status["demo_mode"] and status["live_data"] == "unavailable"
    assert len(client.get("/api/v1/nba/teams").json()) == 4
    assert len(client.get("/api/v1/nfl/players").json()) == 4


def test_reset_delivery_single_use_and_session_revocation(client, account):
    import re

    import httpx

    data, credentials = account
    assert (
        client.post(
            "/api/v1/auth/password-reset", json={"email": credentials["email"]}
        ).status_code
        == 202
    )
    messages = httpx.get("http://127.0.0.1:8025/api/v1/messages").json()["messages"]
    message = next(
        m
        for m in messages
        if any(t["Address"] == credentials["email"] for t in m["To"])
    )
    detail = httpx.get(f"http://127.0.0.1:8025/api/v1/message/{message['ID']}").json()
    token = re.search(r"reset=([A-Za-z0-9_-]+)", detail["Text"]).group(1)
    new_password = "updated-test-password-2026"
    body = {"token": token, "password": new_password}
    assert (
        client.post("/api/v1/auth/password-reset/confirm", json=body).status_code == 204
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.post("/api/v1/auth/password-reset/confirm", json=body).status_code == 400
    )
    assert client.post("/api/v1/auth/login", json=credentials).status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login", json={**credentials, "password": new_password}
        ).status_code
        == 200
    )
    httpx.request(
        "DELETE", "http://127.0.0.1:8025/api/v1/messages", json={"IDs": [message["ID"]]}
    )
