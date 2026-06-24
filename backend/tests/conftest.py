"""Pytest fixtures: in-memory SQLite DB, dependency overrides, test client."""
from __future__ import annotations

import os

os.environ.setdefault("OPENAI_MOCK", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")
# Point the module-level engine at SQLite so importing the app doesn't require
# the Postgres driver. Per-test engines are created in the db_session fixture.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import models  # noqa: F401 — register tables
from app.database.base import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Register + login a user and return Authorization headers."""
    creds = {"email": "user@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=creds)
    resp = client.post("/api/v1/auth/login", json=creds)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
