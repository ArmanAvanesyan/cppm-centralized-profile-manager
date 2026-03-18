"""Dropbox OAuth2: authorization URL and code exchange only."""
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.integrations.oauth.base_oauth import BaseOAuthClient, OAuthTokenResult

DROPBOX_AUTH_BASE = "https://www.dropbox.com/oauth2/authorize"
DROPBOX_TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"


class DropboxOAuthClient(BaseOAuthClient):
    """Dropbox OAuth2 client (auth URL + token exchange). No scope list; uses token_access_type=offline."""

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,  # noqa: ARG002
    ) -> str:
        params = {
            "client_id": settings.DROPBOX_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "token_access_type": "offline",
            "state": state,
        }
        return f"{DROPBOX_AUTH_BASE}?{urlencode(params)}"

    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenResult | None:
        if not settings.DROPBOX_CLIENT_ID or not settings.DROPBOX_CLIENT_SECRET:
            return None
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "client_id": settings.DROPBOX_CLIENT_ID,
            "client_secret": settings.DROPBOX_CLIENT_SECRET,
        }
        try:
            resp = httpx.post(DROPBOX_TOKEN_URL, data=data)
            resp.raise_for_status()
            tok = resp.json()
        except Exception:
            return None
        access = tok.get("access_token")
        if not access:
            return None
        refresh = tok.get("refresh_token")
        # Dropbox tokens are long-lived; no expires_in in typical response
        return OAuthTokenResult(
            access_token=access,
            refresh_token=refresh,
            expires_at=None,
        )
