"""API tests for auth router."""
import hashlib
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from app.core.config import settings
from app.database.models import User
from app.modules.auth.repository import create_email_otp, create_user


def test_signup(client):
    r = client.post("/api/v1/auth/email/signup", json={"email": "signup_api@example.com"})
    assert r.status_code == 200
    assert r.json()["message"] == "OTP sent"


def test_verify_success(client, db_session):
    otp = "111222"
    otp_hash = hashlib.sha256((otp + settings.OTP_SECRET).encode()).hexdigest()
    expires = datetime.now(UTC) + timedelta(minutes=10)
    create_email_otp(db_session, "verify_ok@example.com", otp_hash, expires)
    r = client.post("/api/v1/auth/email/verify", json={"email": "verify_ok@example.com", "otp": otp})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_verify_invalid_otp(client):
    r = client.post(
        "/api/v1/auth/email/verify",
        json={"email": "invalid@example.com", "otp": "000000"},
    )
    assert r.status_code == 400


def test_google_login_success(client, db_session):  # noqa: ARG001
    with (
        patch("app.modules.auth.service.settings") as mock_settings,
        patch("app.modules.auth.service.google_id_token.verify_oauth2_token") as mock_verify,
    ):
        mock_settings.GOOGLE_CLIENT_ID = "cid"
        mock_verify.return_value = {"email": "g@example.com", "sub": "g-sub"}
        r = client.post("/api/v1/auth/google", json={"id_token": "fake"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_google_login_invalid(client):
    with patch("app.modules.auth.service.settings") as mock_settings:
        mock_settings.GOOGLE_CLIENT_ID = "cid"
        with patch("app.modules.auth.service.google_id_token.verify_oauth2_token") as mock_verify:
            mock_verify.side_effect = ValueError("invalid")
            r = client.post("/api/v1/auth/google", json={"id_token": "bad"})
    assert r.status_code == 401


def test_me(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="me_router@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    r = client_with_auth.get("/api/v1/auth/me")
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "me_router@example.com"
    assert data["user_id"] == str(auth_user_id)


def test_refresh_success(client, db_session):
    from app.modules.auth.repository import create_session
    from app.modules.auth.service import _hash_refresh_token
    user = create_user(db_session, "refresh_api@example.com")
    refresh_token = "secret_refresh_123"
    h = _hash_refresh_token(refresh_token)
    expires = datetime.now(UTC) + timedelta(days=7)
    create_session(db_session, user.user_id, h, expires)
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_refresh_invalid(client):
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
    assert r.status_code == 401


def test_logout(client, db_session):
    from app.modules.auth.repository import create_session
    from app.modules.auth.service import _hash_refresh_token
    user = create_user(db_session, "logout_api@example.com")
    refresh_token = "logout_refresh"
    h = _hash_refresh_token(refresh_token)
    expires = datetime.now(UTC) + timedelta(days=7)
    create_session(db_session, user.user_id, h, expires)
    r = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert r.status_code == 204
