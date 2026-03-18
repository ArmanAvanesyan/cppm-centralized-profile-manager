"""Unit tests for app.modules.auth.repository."""
import uuid
from datetime import UTC, datetime, timedelta

from app.modules.auth.repository import (
    create_auth_provider,
    create_email_otp,
    create_session,
    create_user,
    delete_session,
    get_auth_provider_by_provider_user,
    get_session_by_refresh_hash,
    get_user_by_email,
    get_user_by_id,
    get_valid_otp,
    list_provider_names_by_user_id,
    mark_otp_used,
)
from sqlalchemy.orm import Session


def test_create_user(db_session: Session):
    user = create_user(db_session, "test@example.com")
    assert user.user_id is not None
    assert user.email == "test@example.com"
    assert user.email_verified is False


def test_get_user_by_email(db_session: Session):
    create_user(db_session, "lookup@example.com")
    user = get_user_by_email(db_session, "lookup@example.com")
    assert user is not None
    assert user.email == "lookup@example.com"
    assert get_user_by_email(db_session, "missing@example.com") is None


def test_get_user_by_id(db_session: Session):
    user = create_user(db_session, "id@example.com")
    found = get_user_by_id(db_session, user.user_id)
    assert found is not None
    assert found.user_id == user.user_id
    assert get_user_by_id(db_session, uuid.uuid4()) is None


def test_create_auth_provider(db_session: Session):
    user = create_user(db_session, "provider@example.com")
    row = create_auth_provider(db_session, user.user_id, "google", "google-123")
    assert row.provider_id is not None
    assert row.user_id == user.user_id
    assert row.provider == "google"
    assert row.provider_user_id == "google-123"


def test_get_auth_provider_by_provider_user(db_session: Session):
    user = create_user(db_session, "auth@example.com")
    create_auth_provider(db_session, user.user_id, "microsoft", "ms-456")
    auth = get_auth_provider_by_provider_user(db_session, "microsoft", "ms-456")
    assert auth is not None
    assert auth.user_id == user.user_id
    assert get_auth_provider_by_provider_user(db_session, "microsoft", "other") is None


def test_list_provider_names_by_user_id(db_session: Session):
    user = create_user(db_session, "list@example.com")
    create_auth_provider(db_session, user.user_id, "google", "g1")
    create_auth_provider(db_session, user.user_id, "linkedin", "li1")
    names = list_provider_names_by_user_id(db_session, user.user_id)
    assert set(names) == {"google", "linkedin"}
    assert list_provider_names_by_user_id(db_session, uuid.uuid4()) == []


def test_create_email_otp(db_session: Session):
    expires = datetime.now(UTC) + timedelta(minutes=10)
    row = create_email_otp(db_session, "otp@example.com", "hash123", expires)
    assert row.otp_id is not None
    assert row.email == "otp@example.com"
    assert row.otp_hash == "hash123"
    assert row.used is False


def test_get_valid_otp(db_session: Session):
    expires = datetime.now(UTC) + timedelta(minutes=10)
    row = create_email_otp(db_session, "valid@example.com", "h", expires)
    found = get_valid_otp(db_session, "valid@example.com", "h")
    assert found is not None
    assert found.otp_id == row.otp_id
    assert get_valid_otp(db_session, "valid@example.com", "wrong") is None


def test_get_valid_otp_expired(db_session: Session):
    expired = datetime.now(UTC) - timedelta(minutes=1)
    create_email_otp(db_session, "exp@example.com", "h", expired)
    assert get_valid_otp(db_session, "exp@example.com", "h") is None


def test_mark_otp_used(db_session: Session):
    expires = datetime.now(UTC) + timedelta(minutes=10)
    row = create_email_otp(db_session, "used@example.com", "h", expires)
    mark_otp_used(db_session, row.otp_id)
    assert get_valid_otp(db_session, "used@example.com", "h") is None


def test_create_session(db_session: Session):
    user = create_user(db_session, "session@example.com")
    expires = datetime.now(UTC) + timedelta(days=7)
    row = create_session(db_session, user.user_id, "refresh_hash_abc", expires)
    assert row.session_id is not None
    assert row.user_id == user.user_id
    assert row.refresh_token_hash == "refresh_hash_abc"


def test_get_session_by_refresh_hash(db_session: Session):
    user = create_user(db_session, "sess2@example.com")
    expires = datetime.now(UTC) + timedelta(days=7)
    create_session(db_session, user.user_id, "unique_hash", expires)
    session = get_session_by_refresh_hash(db_session, "unique_hash")
    assert session is not None
    assert session.user_id == user.user_id
    assert get_session_by_refresh_hash(db_session, "missing") is None


def test_delete_session(db_session: Session):
    user = create_user(db_session, "del@example.com")
    expires = datetime.now(UTC) + timedelta(days=7)
    row = create_session(db_session, user.user_id, "to_delete_hash", expires)
    delete_session(db_session, row.session_id)
    assert get_session_by_refresh_hash(db_session, "to_delete_hash") is None
