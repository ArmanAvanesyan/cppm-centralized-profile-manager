"""API tests for encryption router."""
from app.database.models import User


def test_encryption_status_not_initialized(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="enc_status_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.get("/api/v1/encryption/status")
    assert r.status_code == 200
    assert r.json()["initialized"] is False
    assert r.json()["key_version"] is None


def test_encryption_init(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="enc_init_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post("/api/v1/encryption/init", json={"password": "secret"})
    assert r.status_code == 200
    assert r.json()["status"] == "initialized"


def test_encryption_rotate(client_with_auth, db_session, auth_user_id):
    from app.modules.encryption.service import init_encryption

    user = User(user_id=auth_user_id, email="enc_rotate_api@example.com")
    db_session.add(user)
    db_session.commit()
    init_encryption(db_session, auth_user_id, "pwd")
    r = client_with_auth.post("/api/v1/encryption/rotate")
    assert r.status_code == 200
    assert r.json()["status"] == "rotated"


def test_encryption_rotate_not_initialized(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="enc_rotate_no_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post("/api/v1/encryption/rotate")
    assert r.status_code == 400
