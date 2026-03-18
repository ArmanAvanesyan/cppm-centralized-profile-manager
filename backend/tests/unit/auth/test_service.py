"""Unit tests for app.modules.auth.service."""
from unittest.mock import Mock, patch

from app.modules.auth.repository import create_user
from app.modules.auth.service import (
    email_signup,
    email_verify,
    get_me,
    google_login,
    linkedin_login,
    logout,
    microsoft_login,
    refresh_tokens,
)


def test_email_signup(db_session):
    email_signup(db_session, "signup@example.com")
    from app.modules.auth.repository import get_valid_otp
    from app.core.config import settings
    import hashlib
    otp_hash = hashlib.sha256(("000000" + settings.OTP_SECRET).encode()).hexdigest()
    # We don't know the OTP (random), so just check that an OTP row exists for the email
    from app.database.models import EmailOtp
    row = db_session.query(EmailOtp).filter(EmailOtp.email == "signup@example.com").first()
    assert row is not None
    assert row.used is False


def test_email_verify_success_new_user(db_session):
    from app.core.config import settings
    import hashlib
    from datetime import datetime, timedelta, timezone
    from app.modules.auth.repository import create_email_otp
    otp = "123456"
    otp_hash = hashlib.sha256((otp + settings.OTP_SECRET).encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    create_email_otp(db_session, "verify_new@example.com", otp_hash, expires)
    result = email_verify(db_session, "verify_new@example.com", otp)
    assert result is not None
    access, refresh = result
    assert isinstance(access, str)
    assert isinstance(refresh, str)


def test_email_verify_invalid_otp(db_session):
    result = email_verify(db_session, "nonexistent@example.com", "000000")
    assert result is None


def test_email_verify_existing_user(db_session):
    from app.modules.auth.repository import create_user, create_email_otp
    from app.core.config import settings
    import hashlib
    from datetime import datetime, timedelta, timezone
    create_user(db_session, "existing_verify@example.com")
    otp = "654321"
    otp_hash = hashlib.sha256((otp + settings.OTP_SECRET).encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    create_email_otp(db_session, "existing_verify@example.com", otp_hash, expires)
    result = email_verify(db_session, "existing_verify@example.com", otp)
    assert result is not None


def test_refresh_tokens_success(db_session):
    from app.modules.auth.repository import create_user, create_session
    from app.modules.auth.service import _hash_refresh_token
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings
    user = create_user(db_session, "refresh@example.com")
    refresh_token = "my_refresh_token_value"
    refresh_hash = _hash_refresh_token(refresh_token)
    expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_session(db_session, user.user_id, refresh_hash, expires)
    result = refresh_tokens(db_session, refresh_token)
    assert result is not None
    access, new_refresh = result
    assert access
    assert new_refresh != refresh_token


def test_refresh_tokens_invalid(db_session):
    assert refresh_tokens(db_session, "invalid_refresh") is None


def test_logout_found(db_session):
    from app.modules.auth.repository import create_user, create_session
    from app.modules.auth.service import _hash_refresh_token
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings
    user = create_user(db_session, "logout@example.com")
    refresh_token = "logout_token"
    refresh_hash = _hash_refresh_token(refresh_token)
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    create_session(db_session, user.user_id, refresh_hash, expires)
    assert logout(db_session, refresh_token) is True
    assert logout(db_session, refresh_token) is False


def test_logout_none_token(db_session):
    assert logout(db_session, None) is False


def test_get_me(db_session):
    user = create_user(db_session, "me@example.com")
    data = get_me(db_session, user)
    assert data["user_id"] == str(user.user_id)
    assert data["email"] == "me@example.com"
    assert data["providers"] == []


@patch("app.modules.auth.service.settings")
@patch("app.modules.auth.service.google_id_token.verify_oauth2_token")
def test_google_login_success(mock_verify, mock_settings, db_session):
    mock_settings.GOOGLE_CLIENT_ID = "client-id"
    mock_verify.return_value = {"email": "google@example.com", "sub": "google-sub-1"}
    result = google_login(db_session, "fake_id_token")
    assert result is not None
    access, refresh = result
    assert access and refresh


@patch("app.modules.auth.service.settings")
def test_google_login_no_client_id(mock_settings, db_session):
    mock_settings.GOOGLE_CLIENT_ID = ""
    assert google_login(db_session, "token") is None


@patch("app.modules.auth.service.settings")
@patch("app.modules.auth.service.google_id_token.verify_oauth2_token")
def test_google_login_verify_fails(mock_verify, mock_settings, db_session):
    mock_settings.GOOGLE_CLIENT_ID = "client-id"
    mock_verify.side_effect = ValueError("invalid token")
    assert google_login(db_session, "bad_token") is None


@patch("app.modules.auth.service.httpx.get")
def test_microsoft_login_success(mock_get, db_session):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "ms-1", "mail": "ms@example.com"}
    mock_get.return_value = mock_resp
    result = microsoft_login(db_session, "fake_access_token")
    assert result is not None


@patch("app.modules.auth.service.httpx.get")
def test_microsoft_login_bad_response(mock_get, db_session):
    mock_resp = Mock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp
    assert microsoft_login(db_session, "token") is None


@patch("app.modules.auth.service.httpx.get")
def test_linkedin_login_success(mock_get, db_session):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"sub": "li-1", "email": "li@example.com"}
    mock_get.return_value = mock_resp
    result = linkedin_login(db_session, "fake_access_token")
    assert result is not None


@patch("app.modules.auth.service.httpx.get")
def test_linkedin_login_no_sub(mock_get, db_session):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {}
    mock_get.return_value = mock_resp
    assert linkedin_login(db_session, "token") is None
