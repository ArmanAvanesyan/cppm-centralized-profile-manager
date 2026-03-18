"""Unit tests for app.modules.encryption.service."""
from app.modules.auth.repository import create_user
from app.modules.encryption.service import get_status, init_encryption, rotate_key


def test_get_status_not_initialized(db_session):
    user = create_user(db_session, "enc_status@example.com")
    data = get_status(db_session, user.user_id)
    assert data["initialized"] is False
    assert data["key_version"] is None


def test_init_encryption(db_session):
    user = create_user(db_session, "enc_init@example.com")
    ok = init_encryption(db_session, user.user_id, "password123")
    assert ok is True
    data = get_status(db_session, user.user_id)
    assert data["initialized"] is True
    assert data["key_version"] == 1


def test_rotate_key(db_session):
    user = create_user(db_session, "enc_rotate@example.com")
    init_encryption(db_session, user.user_id, "pwd")
    ok = rotate_key(db_session, user.user_id)
    assert ok is True
    data = get_status(db_session, user.user_id)
    assert data["key_version"] == 2


def test_rotate_key_not_initialized(db_session):
    user = create_user(db_session, "enc_rotate_no@example.com")
    assert rotate_key(db_session, user.user_id) is False
