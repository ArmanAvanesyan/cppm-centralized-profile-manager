"""Unit tests for app.modules.cloud_storage.repository."""
from datetime import UTC, datetime

from app.modules.auth.repository import create_user
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
    get_storage_folder_by_account,
    get_user_cloud_account_by_user_and_provider,
    list_accounts_by_user,
    update_user_cloud_account,
)
from sqlalchemy.orm import Session


def test_get_cloud_provider_by_name(db_session: Session):
    g = get_cloud_provider_by_name(db_session, "google_drive")
    assert g is not None
    assert g.name == "google_drive"
    assert get_cloud_provider_by_name(db_session, "nonexistent") is None


def test_create_user_cloud_account(db_session: Session):
    user = create_user(db_session, "cloud@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    assert prov is not None
    account = create_user_cloud_account(
        db_session,
        user_id=user.user_id,
        provider_id=prov.provider_id,
        external_account_id="ext-1",
    )
    assert account.account_id is not None
    assert account.user_id == user.user_id
    assert account.provider_id == prov.provider_id


def test_get_user_cloud_account_by_user_and_provider(db_session: Session):
    user = create_user(db_session, "lookup@example.com")
    prov = get_cloud_provider_by_name(db_session, "dropbox")
    create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    found = get_user_cloud_account_by_user_and_provider(
        db_session, user.user_id, "dropbox"
    )
    assert found is not None
    assert get_user_cloud_account_by_user_and_provider(
        db_session, user.user_id, "google_drive"
    ) is None


def test_get_storage_folder_by_account(db_session: Session):
    user = create_user(db_session, "folder@example.com")
    prov = get_cloud_provider_by_name(db_session, "onedrive")
    account = create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    assert get_storage_folder_by_account(db_session, account.account_id) is None


def test_get_or_create_storage_folder(db_session: Session):
    user = create_user(db_session, "create_folder@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    account = create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    folder = get_or_create_storage_folder(
        db_session, account.account_id, "provider_folder_1", "/CPPM"
    )
    assert folder.folder_id is not None
    assert folder.account_id == account.account_id
    assert folder.provider_folder_id == "provider_folder_1"
    folder2 = get_or_create_storage_folder(
        db_session, account.account_id, "updated_id", "/CPPM"
    )
    assert folder2.folder_id == folder.folder_id
    assert folder2.provider_folder_id == "updated_id"


def test_list_accounts_by_user(db_session: Session):
    user = create_user(db_session, "list_acc@example.com")
    g = get_cloud_provider_by_name(db_session, "google_drive")
    d = get_cloud_provider_by_name(db_session, "dropbox")
    create_user_cloud_account(db_session, user.user_id, g.provider_id)
    create_user_cloud_account(db_session, user.user_id, d.provider_id)
    accounts = list_accounts_by_user(db_session, user.user_id)
    assert len(accounts) == 2


def test_update_user_cloud_account(db_session: Session):
    user = create_user(db_session, "upd@example.com")
    prov = get_cloud_provider_by_name(db_session, "google_drive")
    account = create_user_cloud_account(db_session, user.user_id, prov.provider_id)
    updated = update_user_cloud_account(
        db_session,
        account.account_id,
        access_token_encrypted="encrypted_token",
        token_expires_at=datetime.now(UTC),
    )
    assert updated is not None
    db_session.refresh(account)
    assert account.access_token_encrypted == "encrypted_token"
