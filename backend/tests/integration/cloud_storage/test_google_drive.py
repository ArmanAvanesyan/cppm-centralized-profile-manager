"""Integration tests for Google Drive cloud storage (HTTP mocked)."""
from unittest.mock import Mock, patch

from app.modules.auth.repository import create_user
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
)


@patch("app.integrations.oauth.google_oauth.httpx.post")
def test_google_drive_callback_flow(mock_httpx_post, db_session):
    """Simulate callback: token exchange (mocked) then create account and folder."""
    mock_resp = Mock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json.return_value = {
        "access_token": "at",
        "refresh_token": "rt",
        "expires_in": 3600,
    }
    mock_httpx_post.return_value = mock_resp
    user = create_user(db_session, "gdrive_cb@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    account = create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    folder = get_or_create_storage_folder(
        db_session, account.account_id, "drive_folder_id", "/CPPM"
    )
    assert folder.provider_folder_id == "drive_folder_id"
    assert account.account_id is not None
