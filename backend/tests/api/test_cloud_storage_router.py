"""API tests for cloud_storage router."""
from unittest.mock import patch

from app.database.models import User


def test_connect_invalid_provider(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="storage@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post("/api/v1/storage/connect/invalid_provider")
    assert r.status_code == 400


@patch("app.integrations.cloud_storage.google_drive.get_auth_url")
def test_connect_google(client_with_auth, db_session, auth_user_id, mock_get_auth_url):
    user = User(user_id=auth_user_id, email="storage_google@example.com")
    db_session.add(user)
    db_session.commit()
    mock_get_auth_url.return_value = "https://accounts.google.com/o/oauth2/auth"
    r = client_with_auth.post("/api/v1/storage/connect/google")
    assert r.status_code == 200
    assert "auth_url" in r.json()
    assert "google.com" in r.json()["auth_url"]


def test_callback_missing_code(client):
    r = client.get("/api/v1/storage/callback/google")
    assert r.status_code == 400


def test_callback_invalid_provider(client):
    r = client.get("/api/v1/storage/callback/invalid?code=abc")
    assert r.status_code == 400


@patch("app.integrations.cloud_storage.google_drive.handle_callback")
def test_callback_google_success(mock_callback, client, db_session):  # noqa: ARG001
    mock_callback.return_value = True
    r = client.get("/api/v1/storage/callback/google?code=test_code&state=00000000-0000-0000-0000-000000000001")
    assert r.status_code == 200
    assert r.json()["status"] == "connected"


def test_list_accounts(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="list_storage@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.get("/api/v1/storage/accounts")
    assert r.status_code == 200
    assert r.json() == []
