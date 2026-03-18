"""Microsoft OAuth2: authorization URL, code exchange, and token refresh only."""
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.integrations.oauth.base_oauth import BaseOAuthClient, OAuthTokenResult
from app.integrations.oauth.constants import MICROSOFT_SCOPES_STORAGE


def _tenant() -> str:
    return settings.MICROSOFT_TENANT_ID or "common"


def _auth_url_base() -> str:
    return f"https://login.microsoftonline.com/{_tenant()}/oauth2/v2.0/authorize"


def _token_url() -> str:
    return f"https://login.microsoftonline.com/{_tenant()}/oauth2/v2.0/token"


class MicrosoftOAuthClient(BaseOAuthClient):
    """Microsoft OAuth2 client (auth URL + token exchange + refresh). No DB or Graph API."""

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
    ) -> str:
        scopes = scopes or MICROSOFT_SCOPES_STORAGE
        params = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
        }
        return f"{_auth_url_base()}?{urlencode(params)}"

    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenResult | None:
        if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
            return None
        data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        try:
            resp = httpx.post(_token_url(), data=data)
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
            expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
        return OAuthTokenResult(
            access_token=access,
            refresh_token=refresh,
            expires_at=expires_at,
        )

    def refresh_access_token(self, refresh_token: str) -> OAuthTokenResult | None:
        if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
            return None
        data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            resp = httpx.post(_token_url(), data=data)
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
            expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
        return OAuthTokenResult(
            access_token=access,
            refresh_token=tok.get("refresh_token") or refresh_token,
            expires_at=expires_at,
        )
