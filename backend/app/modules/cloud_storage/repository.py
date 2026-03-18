import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import CloudProvider, StorageFolder, UserCloudAccount


def get_user_cloud_account_by_user_and_provider(
    db: Session, user_id: uuid.UUID, provider_name: str
) -> UserCloudAccount | None:
    """Return UserCloudAccount for the given user and provider name, or None."""
    prov = get_cloud_provider_by_name(db, provider_name)
    if not prov:
        return None
    return (
        db.query(UserCloudAccount)
        .filter(
            UserCloudAccount.user_id == user_id,
            UserCloudAccount.provider_id == prov.provider_id,
        )
        .first()
    )


def update_user_cloud_account(
    db: Session,
    account_id: uuid.UUID,
    **kwargs: str | datetime | None,
) -> UserCloudAccount | None:
    """Update stored tokens and optional fields. Pass only the fields to update."""
    updatable = {
        "access_token_encrypted",
        "refresh_token_encrypted",
        "token_expires_at",
        "external_account_id",
    }
    row = db.get(UserCloudAccount, account_id)
    if not row:
        return None
    for key, value in kwargs.items():
        if key in updatable:
            setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def get_cloud_provider_by_name(db: Session, name: str) -> CloudProvider | None:
    return db.query(CloudProvider).filter(CloudProvider.name == name).first()


def get_storage_folder_by_account(db: Session, account_id: uuid.UUID) -> StorageFolder | None:
    """Return the StorageFolder for this account, or None."""
    return db.query(StorageFolder).filter(StorageFolder.account_id == account_id).first()


def get_or_create_storage_folder(
    db: Session,
    account_id: uuid.UUID,
    provider_folder_id: str,
    folder_path: str,
) -> StorageFolder:
    """Return existing StorageFolder for this account or create one."""
    existing = db.query(StorageFolder).filter(StorageFolder.account_id == account_id).first()
    if existing:
        existing.provider_folder_id = provider_folder_id
        existing.folder_path = folder_path
        db.commit()
        db.refresh(existing)
        return existing
    row = StorageFolder(
        account_id=account_id,
        provider_folder_id=provider_folder_id,
        folder_path=folder_path,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_accounts_by_user(db: Session, user_id: uuid.UUID) -> list[UserCloudAccount]:
    return db.query(UserCloudAccount).filter(UserCloudAccount.user_id == user_id).all()


def create_user_cloud_account(
    db: Session,
    user_id: uuid.UUID,
    provider_id: int,
    external_account_id: str | None = None,
    access_token_encrypted: str | None = None,
    refresh_token_encrypted: str | None = None,
    token_expires_at: datetime | None = None,
) -> UserCloudAccount:
    row = UserCloudAccount(
        user_id=user_id,
        provider_id=provider_id,
        external_account_id=external_account_id,
        access_token_encrypted=access_token_encrypted,
        refresh_token_encrypted=refresh_token_encrypted,
        token_expires_at=token_expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
