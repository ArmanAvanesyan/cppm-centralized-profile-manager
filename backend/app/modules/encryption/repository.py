import uuid

from sqlalchemy.orm import Session

from app.database.models import EncryptionKey, EncryptedToken


def get_latest_key(db: Session, user_id: uuid.UUID) -> EncryptionKey | None:
    return (
        db.query(EncryptionKey)
        .filter(EncryptionKey.user_id == user_id)
        .order_by(EncryptionKey.key_version.desc())
        .first()
    )


def create_encryption_key(
    db: Session, user_id: uuid.UUID, encrypted_key: str, key_version: int = 1
) -> EncryptionKey:
    row = EncryptionKey(
        user_id=user_id,
        encrypted_key=encrypted_key,
        key_version=key_version,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
