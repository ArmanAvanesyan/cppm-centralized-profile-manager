"""LinkedIn OAuth2 (OpenID Connect): authorization URL and code exchange only."""
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.integrations.oauth.base_oauth import BaseOAuthClient, OAuthTokenResult
from app.integrations.oauth.constants import LINKEDIN_SCOPES_SIGNIN

LINKEDIN_AUTH_BASE = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class LinkedInOAuthClient(BaseOAuthClient):
    """LinkedIn OAuth2 client (auth URL + token exchange). No refresh in standard flow."""

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
    ) -> str:
        scopes = scopes or LINKEDIN_SCOPES_SIGNIN
        params = {
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
        }
        return f"{LINKEDIN_AUTH_BASE}?{urlencode(params)}"

    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenResult | None:
        if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
            return None
        data = {
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        try:
            resp = httpx.post(LINKEDIN_TOKEN_URL, data=data)
            resp.raise_for_status()
            tok = resp.json()
        except Exception:
            return None
        access = tok.get("access_token")
        if not access:
            return None
        # LinkedIn may return refresh_token in some flows; expires_in is common
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
