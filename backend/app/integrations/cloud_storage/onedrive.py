"""OneDrive OAuth + Microsoft Graph: auth URL, callback (exchange via oauth layer, create CPPM folder + profile.json)."""

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
from app.integrations.oauth.constants import MICROSOFT_SCOPES_STORAGE
from app.modules.cloud_storage.repository import (
    create_user_cloud_account,
    get_cloud_provider_by_name,
    get_or_create_storage_folder,
    get_user_cloud_account_by_user_and_provider,
    update_user_cloud_account,
)


def _storage_redirect_uri() -> str:
    return f"{settings.STORAGE_CALLBACK_BASE_URL.rstrip('/')}/onedrive"


class OneDriveClient(BaseStorageClient):
    def get_auth_url(self, db: Session, user_id: uuid.UUID) -> str:  # noqa: ARG002
        """Build Microsoft OAuth2 authorization URL via oauth layer for OneDrive (Graph)."""
        return get_oauth_client("microsoft").get_authorization_url(
            redirect_uri=_storage_redirect_uri(),
            state=str(user_id),
            scopes=MICROSOFT_SCOPES_STORAGE,
        )

    def handle_callback(
        self,
        db: Session,
        code: str,
        state: str | None,
        user_id: uuid.UUID | None,
    ) -> bool:
        """Exchange code via oauth layer, upsert account, create CPPM folder and profile.json via Graph."""
        if state and not user_id:
            with contextlib.suppress(ValueError):
                user_id = uuid.UUID(state)
        if not user_id:
            return False

        redirect_uri = _storage_redirect_uri()
        result = get_oauth_client("microsoft").exchange_code_for_tokens(
            code=code, redirect_uri=redirect_uri
        )
        if not result:
            return False

        access = result.access_token
        refresh = result.refresh_token
        token_expires_at = result.expires_at

        prov = get_cloud_provider_by_name(db, "onedrive")
        if not prov:
            return False

        existing = get_user_cloud_account_by_user_and_provider(db, user_id, "onedrive")
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
                "https://graph.microsoft.com/v1.0/me/drive/root/children",
                headers=headers,
                json={"name": CPPM_FOLDER_NAME, "folder": {}},
            )
            folder_resp.raise_for_status()
            folder_data = folder_resp.json()
            folder_id = folder_data.get("id")
            if not folder_id:
                return True
        except Exception:
            return True

        with contextlib.suppress(Exception):
            httpx.put(
                f"https://graph.microsoft.com/v1.0/me/drive/root:/{CPPM_FOLDER_NAME}/{PROFILE_FILENAME}:/content",
                headers=headers,
                content=b"{}",
            )

        get_or_create_storage_folder(
            db,
            account_id=account_id,
            provider_folder_id=folder_id,
            folder_path=CPPM_FOLDER_NAME,
        )
        return True


def get_valid_access_token(db: Session, account: UserCloudAccount) -> str | None:
    """Return a valid access token, refreshing via oauth layer if expired (60s buffer)."""
    now = datetime.now(UTC)
    if account.token_expires_at and account.token_expires_at > now + timedelta(seconds=60):
        return account.access_token_encrypted
    if not account.refresh_token_encrypted:
        return account.access_token_encrypted
    result = get_oauth_client("microsoft").refresh_access_token(account.refresh_token_encrypted)
    if not result:
        return account.access_token_encrypted
    update_user_cloud_account(
        db,
        account.account_id,
        access_token_encrypted=result.access_token,
        token_expires_at=result.expires_at,
    )
    return result.access_token


def list_folder_files(db: Session, account: UserCloudAccount, folder_path: str) -> list[dict]:
    """List files in an OneDrive folder by path (e.g. CPPM). Returns list of dicts with id, name."""
    access = get_valid_access_token(db, account)
    if not access:
        return []
    path = folder_path.strip("/") or CPPM_FOLDER_NAME
    try:
        resp = httpx.get(
            f"https://graph.microsoft.com/v1.0/me/drive/root:/{path}:/children",
            headers={"Authorization": f"Bearer {access}"},
            params={"$select": "id,name,size,file"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("value", [])
    except Exception:
        return []


def upload_file_content(
    db: Session,
    account: UserCloudAccount,
    folder_path: str,
    file_name: str,
    content: bytes,
) -> str | None:
    """Upload a file to an OneDrive folder. Returns item id or None."""
    access = get_valid_access_token(db, account)
    if not access:
        return None
    path = folder_path.strip("/") or CPPM_FOLDER_NAME
    item_path = f"{path}/{file_name}"
    try:
        resp = httpx.put(
            f"https://graph.microsoft.com/v1.0/me/drive/root:/{item_path}:/content",
            headers={
                "Authorization": f"Bearer {access}",
                "Content-Type": "application/octet-stream",
            },
            content=content,
        )
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception:
        return None


def download_file_content(db: Session, account: UserCloudAccount, file_path: str) -> bytes | None:
    """Download file content from OneDrive by path (e.g. CPPM/profile.json)."""
    access = get_valid_access_token(db, account)
    if not access:
        return None
    path = file_path.strip("/")
    try:
        resp = httpx.get(
            f"https://graph.microsoft.com/v1.0/me/drive/root:/{path}",
            headers={"Authorization": f"Bearer {access}"},
        )
        resp.raise_for_status()
        download_url = resp.json().get("@microsoft.graph.downloadUrl")
        if not download_url:
            return None
        down = httpx.get(download_url)
        down.raise_for_status()
        return down.content
    except Exception:
        return None


def get_auth_url(db: Session, user_id: uuid.UUID) -> str:
    return OneDriveClient().get_auth_url(db, user_id)


def handle_callback(db: Session, code: str, state: str | None, user_id: uuid.UUID | None) -> bool:
    return OneDriveClient().handle_callback(db, code, state, user_id)
