import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.database.models import AuthProvider, EmailOtp, User
from app.database.models.auth import Session as SessionModel


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str) -> User:
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_auth_provider(
    db: Session,
    user_id: uuid.UUID,
    provider: str,
    provider_user_id: str,
) -> AuthProvider:
    row = AuthProvider(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_auth_provider_by_provider_user(
    db: Session, provider: str, provider_user_id: str
) -> AuthProvider | None:
    return (
        db.query(AuthProvider)
        .filter(
            AuthProvider.provider == provider,
            AuthProvider.provider_user_id == provider_user_id,
        )
        .first()
    )


def list_provider_names_by_user_id(db: Session, user_id: uuid.UUID) -> list[str]:
    rows = db.query(AuthProvider.provider).filter(AuthProvider.user_id == user_id).all()
    return [r[0] for r in rows]


def create_email_otp(
    db: Session, email: str, otp_hash: str, expires_at: datetime
) -> EmailOtp:
    row = EmailOtp(email=email, otp_hash=otp_hash, expires_at=expires_at)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_valid_otp(db: Session, email: str, otp_hash: str) -> EmailOtp | None:
    now = datetime.now(UTC)
    return (
        db.query(EmailOtp)
        .filter(
            EmailOtp.email == email,
            EmailOtp.otp_hash == otp_hash,
            EmailOtp.used == False,  # noqa: E712
            EmailOtp.expires_at > now,
        )
        .first()
    )


def mark_otp_used(db: Session, otp_id: uuid.UUID) -> None:
    row = db.get(EmailOtp, otp_id)
    if row:
        row.used = True
        db.commit()


def create_session(
    db: Session,
    user_id: uuid.UUID,
    refresh_token_hash: str,
    expires_at: datetime,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> SessionModel:
    row = SessionModel(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_session_by_refresh_hash(
    db: Session, refresh_token_hash: str
) -> SessionModel | None:
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.refresh_token_hash == refresh_token_hash,
            SessionModel.expires_at > datetime.now(UTC),
        )
        .first()
    )


def delete_session(db: Session, session_id: uuid.UUID) -> None:
    row = db.get(SessionModel, session_id)
    if row:
        db.delete(row)
        db.commit()
