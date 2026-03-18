import uuid

from sqlalchemy.orm import Session

from app.database.models import CloudProvider
from app.integrations.cloud_storage.constants import CPPM_FOLDER_NAME
from app.modules.cloud_storage.repository import (
    get_storage_folder_by_account,
    get_user_cloud_account_by_user_and_provider,
    list_accounts_by_user,
)

_PROVIDER_TO_DB_NAME = {"google": "google_drive", "onedrive": "onedrive", "dropbox": "dropbox"}


def get_connect_url(db: Session, provider: str, user_id: uuid.UUID) -> str:
    """Return OAuth auth_url for the given provider. Dispatches to integration client."""
    provider = provider.lower()
    if provider == "google":
        from app.integrations.cloud_storage.google_drive import get_auth_url
        return get_auth_url(db, user_id)
    if provider == "dropbox":
        from app.integrations.cloud_storage.dropbox import get_auth_url
        return get_auth_url(db, user_id)
    if provider == "onedrive":
        from app.integrations.cloud_storage.onedrive import get_auth_url
        return get_auth_url(db, user_id)
    raise ValueError(f"Unknown provider: {provider}")


def handle_callback(
    db: Session, provider: str, code: str, state: str | None, user_id: uuid.UUID | None
) -> bool:
    """Exchange code for tokens, create/update account, create CPPM folder. Returns True on success."""
    provider = provider.lower()
    if provider == "google":
        from app.integrations.cloud_storage.google_drive import handle_callback as do_callback
        return do_callback(db, code, state, user_id)
    if provider == "dropbox":
        from app.integrations.cloud_storage.dropbox import handle_callback as do_callback
        return do_callback(db, code, state, user_id)
    if provider == "onedrive":
        from app.integrations.cloud_storage.onedrive import handle_callback as do_callback
        return do_callback(db, code, state, user_id)
    return False


def list_accounts(db: Session, user_id: uuid.UUID) -> list[dict]:
    """List connected cloud accounts for user with provider name and connected_at."""
    accounts = list_accounts_by_user(db, user_id)
    provider_names: dict[int, str] = {}
    for a in accounts:
        if a.provider_id not in provider_names:
            prov = db.get(CloudProvider, a.provider_id)
            if prov:
                provider_names[a.provider_id] = prov.name
    return [
        {"provider": provider_names.get(a.provider_id, "unknown"), "connected_at": a.connected_at}
        for a in accounts
    ]


def list_files_in_cppm_folder(
    db: Session, user_id: uuid.UUID, provider: str
) -> list[dict]:
    """List files in the user's CPPM folder for the given provider. Returns list of file metadata dicts."""
    p = provider.lower()
    db_name = _PROVIDER_TO_DB_NAME.get(p)
    if not db_name:
        return []
    account = get_user_cloud_account_by_user_and_provider(db, user_id, db_name)
    if not account:
        return []
    folder = get_storage_folder_by_account(db, account.account_id)
    if not folder:
        return []
    if p == "google":
        from app.integrations.cloud_storage.google_drive import list_folder_files
        return list_folder_files(db, account, folder.provider_folder_id or "")
    if p == "onedrive":
        from app.integrations.cloud_storage.onedrive import list_folder_files
        return list_folder_files(db, account, folder.folder_path or CPPM_FOLDER_NAME)
    if p == "dropbox":
        from app.integrations.cloud_storage.dropbox import list_folder_files
        return list_folder_files(db, account, folder.folder_path or f"/{CPPM_FOLDER_NAME}")
    return []


def upload_file_to_cppm(
    db: Session,
    user_id: uuid.UUID,
    provider: str,
    file_name: str,
    content: bytes,
    mime_type: str = "application/octet-stream",
) -> str | None:
    """Upload a file to the user's CPPM folder. Returns file id/path or None."""
    p = provider.lower()
    db_name = _PROVIDER_TO_DB_NAME.get(p)
    if not db_name:
        return None
    account = get_user_cloud_account_by_user_and_provider(db, user_id, db_name)
    if not account:
        return None
    folder = get_storage_folder_by_account(db, account.account_id)
    if not folder:
        return None
    if p == "google":
        from app.integrations.cloud_storage.google_drive import upload_file_content
        return upload_file_content(
            db, account, folder.provider_folder_id or "", file_name, content, mime_type
        )
    if p == "onedrive":
        from app.integrations.cloud_storage.onedrive import upload_file_content
        return upload_file_content(
            db, account, folder.folder_path or CPPM_FOLDER_NAME, file_name, content
        )
    if p == "dropbox":
        from app.integrations.cloud_storage.dropbox import upload_file_content
        return upload_file_content(
            db, account, folder.folder_path or f"/{CPPM_FOLDER_NAME}", file_name, content
        )
    return None


def download_file_from_cppm(
    db: Session, user_id: uuid.UUID, provider: str, file_id_or_path: str
) -> bytes | None:
    """Download a file from the user's CPPM storage. file_id_or_path is Drive file id, or path for OneDrive/Dropbox."""
    p = provider.lower()
    db_name = _PROVIDER_TO_DB_NAME.get(p)
    if not db_name:
        return None
    account = get_user_cloud_account_by_user_and_provider(db, user_id, db_name)
    if not account:
        return None
    if p == "google":
        from app.integrations.cloud_storage.google_drive import download_file_content
        return download_file_content(db, account, file_id_or_path)
    if p == "onedrive":
        from app.integrations.cloud_storage.onedrive import download_file_content
        return download_file_content(db, account, file_id_or_path)
    if p == "dropbox":
        from app.integrations.cloud_storage.dropbox import download_file_content
        return download_file_content(db, account, file_id_or_path)
    return None
