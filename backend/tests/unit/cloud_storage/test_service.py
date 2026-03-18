"""Unit tests for app.modules.cloud_storage.service."""
from unittest.mock import Mock, patch

import pytest
from app.modules.auth.repository import create_user
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
)
from app.modules.cloud_storage.service import (
    get_connect_url,
    handle_callback,
    list_accounts,
    list_files_in_cppm_folder,
)


def test_get_connect_url_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_connect_url(Mock(), "invalid", __import__("uuid").uuid4())


@patch("app.integrations.cloud_storage.google_drive.get_auth_url")
def test_get_connect_url_google(mock_get_auth_url, db_session):
    mock_get_auth_url.return_value = "https://google.com/auth"
    user = create_user(db_session, "google_url@example.com")
    url = get_connect_url(db_session, "google", user.user_id)
    assert url == "https://google.com/auth"


@patch("app.integrations.cloud_storage.dropbox.get_auth_url")
def test_get_connect_url_dropbox(mock_get_auth_url, db_session):
    mock_get_auth_url.return_value = "https://dropbox.com/oauth2/authorize"
    user = create_user(db_session, "d@example.com")
    url = get_connect_url(db_session, "dropbox", user.user_id)
    assert url == "https://dropbox.com/oauth2/authorize"


@patch("app.integrations.cloud_storage.onedrive.get_auth_url")
def test_get_connect_url_onedrive(mock_get_auth_url, db_session):
    mock_get_auth_url.return_value = "https://login.microsoftonline.com/oauth2/v2.0/authorize"
    user = create_user(db_session, "o@example.com")
    url = get_connect_url(db_session, "onedrive", user.user_id)
    assert "microsoftonline.com" in url


def test_handle_callback_unknown_provider():
    assert handle_callback(Mock(), "invalid", "code", None, None) is False


@patch("app.integrations.cloud_storage.google_drive.handle_callback")
def test_handle_callback_google(mock_callback, db_session):
    mock_callback.return_value = True
    user = create_user(db_session, "cb@example.com")
    result = handle_callback(db_session, "google", "code", str(user.user_id), user.user_id)
    assert result is True


def test_list_accounts_empty(db_session):
    user = create_user(db_session, "empty_acc@example.com")
    assert list_accounts(db_session, user.user_id) == []


def test_list_accounts_with_data(db_session):
    user = create_user(db_session, "with_acc@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    items = list_accounts(db_session, user.user_id)
    assert len(items) == 1
    assert items[0]["provider"] == "google_drive"


def test_list_files_in_cppm_folder_unknown_provider(db_session):
    user = create_user(db_session, "files@example.com")
    assert list_files_in_cppm_folder(db_session, user.user_id, "invalid") == []


def test_list_files_in_cppm_folder_no_account(db_session):
    user = create_user(db_session, "no_account@example.com")
    assert list_files_in_cppm_folder(db_session, user.user_id, "google") == []


@patch("app.integrations.cloud_storage.google_drive.list_folder_files")
def test_list_files_in_cppm_folder_google(mock_list, db_session):
    mock_list.return_value = [{"name": "file1.pdf", "id": "id1"}]
    user = create_user(db_session, "gfiles@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    account = create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    get_or_create_storage_folder(db_session, account.account_id, "folder_id", "/CPPM")
    result = list_files_in_cppm_folder(db_session, user.user_id, "google")
    assert result == [{"name": "file1.pdf", "id": "id1"}]
