"""Google OAuth2: authorization URL, code exchange, and token refresh only."""
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.integrations.oauth.base_oauth import BaseOAuthClient, OAuthTokenResult
from app.integrations.oauth.constants import GOOGLE_SCOPES_STORAGE

GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleOAuthClient(BaseOAuthClient):
    """Google OAuth2 client (auth URL + token exchange + refresh). No DB or Drive API."""

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
    ) -> str:
        scopes = scopes or GOOGLE_SCOPES_STORAGE
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{GOOGLE_AUTH_BASE}?{urlencode(params)}"

    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenResult | None:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return None
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        try:
            resp = httpx.post(GOOGLE_TOKEN_URL, data=data)
            resp.raise_for_status()
            tok = resp.json()
        except Exception:
            return None
        access = tok.get("access_token")
        if not access:
            return None
        refresh = tok.get("refresh_token")
        expires_in = tok.get("expires_in")
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        return OAuthTokenResult(
            access_token=access,
            refresh_token=refresh,
            expires_at=expires_at,
        )

    def refresh_access_token(self, refresh_token: str) -> OAuthTokenResult | None:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return None
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            resp = httpx.post(GOOGLE_TOKEN_URL, data=data)
            resp.raise_for_status()
            tok = resp.json()
        except Exception:
            return None
        access = tok.get("access_token")
        if not access:
            return None
        expires_in = tok.get("expires_in")
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        return OAuthTokenResult(
            access_token=access,
            refresh_token=tok.get("refresh_token") or refresh_token,
            expires_at=expires_at,
        )
