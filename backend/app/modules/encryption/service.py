import uuid

from sqlalchemy.orm import Session

from app.modules.encryption.repository import create_encryption_key, get_latest_key


def init_encryption(db: Session, user_id: uuid.UUID, _password: str) -> bool:
    """Derive key from password, store encrypted. Stub: store placeholder."""
    # TODO: use cryptography to derive key from password, encrypt with master key, store
    encrypted_key = "stub_encrypted_key"
    create_encryption_key(db, user_id, encrypted_key, key_version=1)
    return True


def rotate_key(db: Session, user_id: uuid.UUID) -> bool:
    """Create new key version, re-encrypt tokens. Stub."""
    latest = get_latest_key(db, user_id)
    if not latest:
        return False
    create_encryption_key(db, user_id, "stub_rotated", key_version=latest.key_version + 1)
    return True


def get_status(db: Session, user_id: uuid.UUID) -> dict:
    latest = get_latest_key(db, user_id)
    return {
        "initialized": latest is not None,
        "key_version": latest.key_version if latest else None,
    }
