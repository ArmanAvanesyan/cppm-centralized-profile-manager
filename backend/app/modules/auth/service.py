import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.database.models import User
from app.modules.auth.repository import (
    create_auth_provider,
    create_email_otp,
    create_session,
    create_user,
    delete_session,
    get_auth_provider_by_provider_user,
    get_session_by_refresh_hash,
    get_user_by_email,
    get_user_by_id,
    get_valid_otp,
    list_provider_names_by_user_id,
    mark_otp_used,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_otp(otp: str) -> str:
    return hashlib.sha256((otp + settings.OTP_SECRET).encode()).hexdigest()


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _create_tokens(user_id: uuid.UUID) -> tuple[str, str]:
    access = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    refresh = secrets.token_urlsafe(32)
    return access, refresh


def email_signup(db, email: str) -> None:
    """Create and store OTP; in production would send email."""
    otp = "".join(secrets.choice("0123456789") for _ in range(6))
    otp_hash = _hash_otp(otp)
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    create_email_otp(db, email, otp_hash, expires_at)
    # TODO: send email with otp


def email_verify(db, email: str, otp: str) -> tuple[str, str] | None:
    """Verify OTP, get or create user, create session, return (access_token, refresh_token)."""
    otp_hash = _hash_otp(otp)
    row = get_valid_otp(db, email, otp_hash)
    if not row:
        return None
    mark_otp_used(db, row.otp_id)
    user = get_user_by_email(db, email)
    if not user:
        user = create_user(db, email)
    else:
        # Mark email verified if not already
        if not user.email_verified:
            user.email_verified = True
            db.commit()
    access, refresh = _create_tokens(user.user_id)
    refresh_hash = _hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_session(db, user.user_id, refresh_hash, expires_at)
    return access, refresh


def google_login(db, id_token: str) -> tuple[str, str] | None:
    """Verify Google id_token, get or create user and auth_provider, return tokens."""
    if not settings.GOOGLE_CLIENT_ID:
        return None
    try:
        payload = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        email = payload.get("email")
        sub = payload.get("sub")
        if not email or not sub:
            return None
    except Exception:
        return None
    provider = "google"
    auth = get_auth_provider_by_provider_user(db, provider, sub)
    if auth:
        user = get_user_by_id(db, auth.user_id)
    else:
        user = get_user_by_email(db, email)
        if not user:
            user = create_user(db, email)
        create_auth_provider(db, user.user_id, provider, sub)
    if not user:
        return None
    access, refresh = _create_tokens(user.user_id)
    refresh_hash = _hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_session(db, user.user_id, refresh_hash, expires_at)
    return access, refresh


def microsoft_login(db, access_token: str) -> tuple[str, str] | None:
    """Verify Microsoft access_token via Graph /me, get or create user and auth_provider, return tokens."""
    try:
        resp = httpx.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        provider_user_id = data.get("id")
        email = data.get("mail") or data.get("userPrincipalName")
        if not provider_user_id or not email:
            return None
    except Exception:
        return None
    provider = "microsoft"
    auth = get_auth_provider_by_provider_user(db, provider, provider_user_id)
    if auth:
        user = get_user_by_id(db, auth.user_id)
    else:
        user = get_user_by_email(db, email)
        if not user:
            user = create_user(db, email)
        create_auth_provider(db, user.user_id, provider, provider_user_id)
    if not user:
        return None
    access, refresh = _create_tokens(user.user_id)
    refresh_hash = _hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_session(db, user.user_id, refresh_hash, expires_at)
    return access, refresh


def linkedin_login(db, access_token: str) -> tuple[str, str] | None:
    """Verify LinkedIn access_token via userinfo, get or create user and auth_provider, return tokens."""
    try:
        resp = httpx.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        sub = data.get("sub")
        if not sub:
            return None
        email = data.get("email") or f"linkedin_{sub}@users.noreply.cppm"
    except Exception:
        return None
    provider = "linkedin"
    auth = get_auth_provider_by_provider_user(db, provider, sub)
    if auth:
        user = get_user_by_id(db, auth.user_id)
    else:
        user = get_user_by_email(db, email)
        if not user:
            user = create_user(db, email)
        create_auth_provider(db, user.user_id, provider, sub)
    if not user:
        return None
    access, refresh = _create_tokens(user.user_id)
    refresh_hash = _hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_session(db, user.user_id, refresh_hash, expires_at)
    return access, refresh


def refresh_tokens(db, refresh_token: str) -> tuple[str, str] | None:
    """Validate refresh token, issue new access and refresh tokens."""
    refresh_hash = _hash_refresh_token(refresh_token)
    session = get_session_by_refresh_hash(db, refresh_hash)
    if not session:
        return None
    access, new_refresh = _create_tokens(session.user_id)
    new_hash = _hash_refresh_token(new_refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    delete_session(db, session.session_id)
    create_session(db, session.user_id, new_hash, expires_at)
    return access, new_refresh


def logout(db, refresh_token: str | None) -> bool:
    """Invalidate session by refresh token. Returns True if found and deleted."""
    if not refresh_token:
        return False
    refresh_hash = _hash_refresh_token(refresh_token)
    session = get_session_by_refresh_hash(db, refresh_hash)
    if not session:
        return False
    delete_session(db, session.session_id)
    return True


def get_me(db, user: User) -> dict:
    """Return current user info and linked providers for GET /auth/me."""
    providers = list_provider_names_by_user_id(db, user.user_id)
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "providers": providers,
    }
