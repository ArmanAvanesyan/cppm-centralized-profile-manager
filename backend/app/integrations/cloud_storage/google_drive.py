"""Google Drive OAuth + Drive API: auth URL, callback (exchange via oauth layer, create CPPM folder + profile.json)."""

import contextlib
import uuid
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models import UserCloudAccount
from app.integrations.cloud_storage.base_storage import BaseStorageClient
from app.integrations.cloud_storage.constants import CPPM_FOLDER_NAME, PROFILE_FILENAME
from app.integrations.oauth import get_oauth_client
from app.integrations.oauth.constants import GOOGLE_SCOPES_STORAGE
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
    get_user_cloud_account_by_user_and_provider,
    update_user_cloud_account,
)


def _storage_redirect_uri() -> str:
    return f"{settings.STORAGE_CALLBACK_BASE_URL.rstrip('/')}/google"


class GoogleDriveClient(BaseStorageClient):
    def get_auth_url(self, _db: Session, user_id: uuid.UUID) -> str:
        """Build Google OAuth2 authorization URL via oauth layer. state carries user_id for callback."""
        return get_oauth_client("google").get_authorization_url(
            redirect_uri=_storage_redirect_uri(),
            state=str(user_id),
            scopes=GOOGLE_SCOPES_STORAGE,
        )

    def handle_callback(
        self,
        db: Session,
        code: str,
        state: str | None,
        user_id: uuid.UUID | None,
    ) -> bool:
        """Exchange code via oauth layer, upsert UserCloudAccount, create CPPM folder and profile.json via Drive API."""
        if state and not user_id:
            with contextlib.suppress(ValueError):
                user_id = uuid.UUID(state)
        if not user_id:
            return False

        redirect_uri = _storage_redirect_uri()
        result = get_oauth_client("google").exchange_code_for_tokens(
            code=code, redirect_uri=redirect_uri
        )
        if not result:
            return False

        access = result.access_token
        refresh = result.refresh_token
        token_expires_at = result.expires_at

        prov = get_cloud_provider_by_name(db, "google_drive")
        if not prov:
            return False

        existing = get_user_cloud_account_by_user_and_provider(db, user_id, "google_drive")
        if existing:
            update_user_cloud_account(
                db,
                existing.account_id,
                access_token_encrypted=access,
                refresh_token_encrypted=refresh
                if refresh is not None
                else existing.refresh_token_encrypted,
                token_expires_at=token_expires_at,
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
                token_expires_at=token_expires_at,
            )
            account_id = row.account_id

        headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}

        try:
            folder_resp = httpx.post(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                json={
                    "name": CPPM_FOLDER_NAME,
                    "mimeType": "application/vnd.google-apps.folder",
                },
            )
            folder_resp.raise_for_status()
            folder_data = folder_resp.json()
            folder_id = folder_data.get("id")
            if not folder_id:
                return True
        except Exception:
            return True

        try:
            create_resp = httpx.post(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                json={
                    "name": PROFILE_FILENAME,
                    "parents": [folder_id],
                    "mimeType": "application/json",
                },
            )
            create_resp.raise_for_status()
            file_data = create_resp.json()
            file_id = file_data.get("id")
            if file_id:
                httpx.patch(
                    f"https://www.googleapis.com/upload/drive/v3/files/{file_id}",
                    params={"uploadType": "media"},
                    headers={
                        "Authorization": f"Bearer {access}",
                        "Content-Type": "application/json",
                    },
                    content=b"{}",
                )
        except Exception:
            pass

        get_or_create_storage_folder(
            db,
            account_id=account_id,
            provider_folder_id=folder_id,
            folder_path=CPPM_FOLDER_NAME,
        )
        return True


def get_valid_access_token(db: Session, account: UserCloudAccount) -> str | None:
    """Return a valid access token, refreshing via oauth layer and updating DB if expired (with 60s buffer)."""
    now = datetime.now(UTC)
    if account.token_expires_at and account.token_expires_at > now + timedelta(seconds=60):
        return account.access_token_encrypted
    if not account.refresh_token_encrypted:
        return account.access_token_encrypted
    result = get_oauth_client("google").refresh_access_token(account.refresh_token_encrypted)
    if not result:
        return account.access_token_encrypted
    update_user_cloud_account(
        db,
        account.account_id,
        access_token_encrypted=result.access_token,
        token_expires_at=result.expires_at,
    )
    return result.access_token


def list_folder_files(db: Session, account: UserCloudAccount, folder_id: str) -> list[dict]:
    """List files in a Drive folder. Returns list of dicts with id, name, mimeType."""
    access = get_valid_access_token(db, account)
    if not access:
        return []
    try:
        resp = httpx.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {access}"},
            params={"q": f"'{folder_id}' in parents", "fields": "files(id,name,mimeType,size)"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("files", [])
    except Exception:
        return []


def upload_file_content(
    db: Session,
    account: UserCloudAccount,
    folder_id: str,
    file_name: str,
    content: bytes,
    mime_type: str = "application/octet-stream",
) -> str | None:
    """Upload a file to a Drive folder. Returns file id or None."""
    access = get_valid_access_token(db, account)
    if not access:
        return None
    try:
        create_resp = httpx.post(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"},
            json={"name": file_name, "parents": [folder_id], "mimeType": mime_type},
        )
        create_resp.raise_for_status()
        file_id = create_resp.json().get("id")
        if not file_id:
            return None
        httpx.patch(
            f"https://www.googleapis.com/upload/drive/v3/files/{file_id}",
            params={"uploadType": "media"},
            headers={"Authorization": f"Bearer {access}", "Content-Type": mime_type},
            content=content,
        ).raise_for_status()
        return file_id
    except Exception:
        return None


def download_file_content(db: Session, account: UserCloudAccount, file_id: str) -> bytes | None:
    """Download file content from Drive by file id."""
    access = get_valid_access_token(db, account)
    if not access:
        return None
    try:
        resp = httpx.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            params={"alt": "media"},
            headers={"Authorization": f"Bearer {access}"},
        )
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None


# Module-level functions for backward-compatible imports
def get_auth_url(db: Session, user_id: uuid.UUID) -> str:
    return GoogleDriveClient().get_auth_url(db, user_id)


def handle_callback(db: Session, code: str, state: str | None, user_id: uuid.UUID | None) -> bool:
    return GoogleDriveClient().handle_callback(db, code, state, user_id)
