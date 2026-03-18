"""Smoke tests for app.main."""

from app.main import app
from fastapi.testclient import TestClient


def test_health():
    """GET /health returns 200 and status ok."""
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_auth_me_requires_auth(client):
    """GET /api/v1/auth/me without auth returns 401."""
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_profile_requires_auth(client):
    """GET /api/v1/profile without auth returns 401."""
    r = client.get("/api/v1/profile")
    assert r.status_code == 401
