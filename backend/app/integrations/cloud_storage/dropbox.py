"""Dropbox OAuth + API v2: auth URL, callback (exchange via oauth layer, create CPPM folder + profile.json)."""

import contextlib
import json
import uuid

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models import UserCloudAccount
from app.integrations.cloud_storage.base_storage import BaseStorageClient
from app.integrations.cloud_storage.constants import CPPM_FOLDER_NAME, PROFILE_FILENAME
from app.integrations.oauth import get_oauth_client
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
    get_user_cloud_account_by_user_and_provider,
    update_user_cloud_account,
)


def _storage_redirect_uri() -> str:
    return f"{settings.STORAGE_CALLBACK_BASE_URL.rstrip('/')}/dropbox"


class DropboxClient(BaseStorageClient):
    def get_auth_url(self, _db: Session, user_id: uuid.UUID) -> str:
        """Build Dropbox OAuth2 authorization URL via oauth layer."""
        return get_oauth_client("dropbox").get_authorization_url(
            redirect_uri=_storage_redirect_uri(),
            state=str(user_id),
        )

    def handle_callback(
        self,
        db: Session,
        code: str,
        state: str | None,
        user_id: uuid.UUID | None,
    ) -> bool:
        """Exchange code via oauth layer, upsert account, create CPPM folder and profile.json via Dropbox API v2."""
        if state and not user_id:
            with contextlib.suppress(ValueError):
                user_id = uuid.UUID(state)
        if not user_id:
            return False

        redirect_uri = _storage_redirect_uri()
        result = get_oauth_client("dropbox").exchange_code_for_tokens(
            code=code, redirect_uri=redirect_uri
        )
        if not result:
            return False

        access = result.access_token
        refresh = result.refresh_token

        prov = get_cloud_provider_by_name(db, "dropbox")
        if not prov:
            return False

        existing = get_user_cloud_account_by_user_and_provider(db, user_id, "dropbox")
        if existing:
            update_user_cloud_account(
                db,
                existing.account_id,
                access_token_encrypted=access,
                refresh_token_encrypted=refresh
                if refresh is not None
                else existing.refresh_token_encrypted,
            )
            account_id = existing.account_id
        else:
            row = create_user_cloud_account(
                db,
                user_id=user_id,
                provider_id=prov.provider_id,
                external_account_id=None,
                access_token_encrypted=access,
                refresh_token_encrypted=refresh,
            )
            account_id = row.account_id

        cppm_path = f"/{CPPM_FOLDER_NAME}"
        profile_path = f"/{CPPM_FOLDER_NAME}/{PROFILE_FILENAME}"
        headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}

        try:
            folder_resp = httpx.post(
                "https://api.dropboxapi.com/2/files/create_folder_v2",
                headers=headers,
                json={"path": cppm_path, "autorename": False},
            )
            folder_resp.raise_for_status()
            folder_data = folder_resp.json()
            metadata = folder_data.get("metadata") or folder_data.get("folder") or {}
            folder_id = metadata.get("id") or cppm_path
        except Exception:
            folder_id = cppm_path

        with contextlib.suppress(Exception):
            httpx.post(
                "https://content.dropboxapi.com/2/files/upload",
                headers={
                    "Authorization": f"Bearer {access}",
                    "Content-Type": "application/octet-stream",
                    "Dropbox-API-Arg": json.dumps({"path": profile_path, "mode": "overwrite"}),
                },
                content=b"{}",
            )

        get_or_create_storage_folder(
            db,
            account_id=account_id,
            provider_folder_id=folder_id,
            folder_path=cppm_path,
        )
        return True


def list_folder_files(_db: Session, account: UserCloudAccount, folder_path: str) -> list[dict]:
    """List files in a Dropbox folder by path (e.g. /CPPM). Returns list of dicts with id, name."""
    access = account.access_token_encrypted
    if not access:
        return []
    try:
        resp = httpx.post(
            "https://api.dropboxapi.com/2/files/list_folder",
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"},
            json={"path": folder_path or f"/{CPPM_FOLDER_NAME}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("entries", [])
    except Exception:
        return []


def upload_file_content(
    _db: Session,
    account: UserCloudAccount,
    folder_path: str,
    file_name: str,
    content: bytes,
) -> str | None:
    """Upload a file to a Dropbox folder. Returns path or None."""
    access = account.access_token_encrypted
    if not access:
        return None
    path = (
        f"{folder_path.rstrip('/')}/{file_name}"
        if folder_path
        else f"/{CPPM_FOLDER_NAME}/{file_name}"
    )
    try:
        resp = httpx.post(
            "https://content.dropboxapi.com/2/files/upload",
            headers={
                "Authorization": f"Bearer {access}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": json.dumps({"path": path, "mode": "overwrite"}),
            },
            content=content,
        )
        resp.raise_for_status()
        return path
    except Exception:
        return None


def download_file_content(_db: Session, account: UserCloudAccount, file_path: str) -> bytes | None:
    """Download file content from Dropbox by path (e.g. /CPPM/profile.json)."""
    access = account.access_token_encrypted
    if not access:
        return None
    try:
        resp = httpx.post(
            "https://content.dropboxapi.com/2/files/download",
            headers={
                "Authorization": f"Bearer {access}",
                "Dropbox-API-Arg": json.dumps({"path": file_path}),
            },
        )
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None


def get_auth_url(db: Session, user_id: uuid.UUID) -> str:
    return DropboxClient().get_auth_url(db, user_id)


def handle_callback(db: Session, code: str, state: str | None, user_id: uuid.UUID | None) -> bool:
    return DropboxClient().handle_callback(db, code, state, user_id)
