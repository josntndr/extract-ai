"""Auth flow tests: register, login, refresh rotation, RBAC."""
from __future__ import annotations


def test_register_and_login(client):
    creds = {"email": "alice@example.com", "password": "supersecret123", "full_name": "Alice"}
    r = client.post("/api/v1/auth/register", json=creds)
    assert r.status_code == 201
    assert r.json()["email"] == "alice@example.com"
    assert r.json()["role"] == "user"

    r = client.post("/api/v1/auth/login", json={"email": creds["email"], "password": creds["password"]})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_duplicate_registration_rejected(client):
    creds = {"email": "dup@example.com", "password": "supersecret123"}
    assert client.post("/api/v1/auth/register", json=creds).status_code == 201
    assert client.post("/api/v1/auth/register", json=creds).status_code == 409


def test_login_wrong_password(client):
    creds = {"email": "bob@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=creds)
    r = client.post("/api/v1/auth/login", json={"email": creds["email"], "password": "wrong"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "user@example.com"


def test_refresh_token_rotation(client):
    creds = {"email": "rot@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=creds)
    login = client.post("/api/v1/auth/login", json=creds).json()
    old_refresh = login["refresh_token"]

    # First refresh succeeds and returns a new pair.
    r1 = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r1.status_code == 200
    new_refresh = r1.json()["refresh_token"]
    assert new_refresh != old_refresh

    # Reusing the rotated (now-revoked) refresh token is rejected.
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 401


def test_password_is_hashed(client, db_session):
    from sqlalchemy import select

    from app.database.models.user import User

    creds = {"email": "hash@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=creds)
    user = db_session.scalar(select(User).where(User.email == creds["email"]))
    assert user is not None
    assert user.hashed_password != creds["password"]
    assert user.hashed_password.startswith("$2")  # bcrypt
