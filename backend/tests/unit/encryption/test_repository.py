"""Unit tests for app.modules.encryption.repository."""
from app.modules.auth.repository import create_user
from app.modules.encryption.repository import create_encryption_key, get_latest_key


def test_create_encryption_key(db_session):
    user = create_user(db_session, "enc_key@example.com")
    row = create_encryption_key(db_session, user.user_id, "encrypted_data", key_version=1)
    assert row.key_id is not None
    assert row.user_id == user.user_id
    assert row.encrypted_key == "encrypted_data"
    assert row.key_version == 1


def test_get_latest_key_none(db_session):
    user = create_user(db_session, "no_key@example.com")
    assert get_latest_key(db_session, user.user_id) is None


def test_get_latest_key(db_session):
    user = create_user(db_session, "latest_key@example.com")
    create_encryption_key(db_session, user.user_id, "v1", key_version=1)
    create_encryption_key(db_session, user.user_id, "v2", key_version=2)
    latest = get_latest_key(db_session, user.user_id)
    assert latest is not None
    assert latest.key_version == 2
    assert latest.encrypted_key == "v2"
