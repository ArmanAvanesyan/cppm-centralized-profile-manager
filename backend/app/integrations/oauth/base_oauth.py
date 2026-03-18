"""Base interface for OAuth2 providers (auth URL + token exchange + refresh only)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OAuthTokenResult:
    """Result of OAuth token exchange or refresh."""

    access_token: str
    refresh_token: str | None = None
    expires_at: datetime | None = None


class BaseOAuthClient(ABC):
    """Abstract base for OAuth2 clients (Google, Microsoft, LinkedIn, Dropbox)."""

    @abstractmethod
    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
    ) -> str:
        """Return OAuth2 authorization URL. Caller provides redirect_uri and state."""
        ...

    @abstractmethod
    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenResult | None:
        """Exchange authorization code for access (and optionally refresh) tokens."""
        ...

    def refresh_access_token(self, _refresh_token: str) -> OAuthTokenResult | None:
        """Refresh access token using refresh_token. Override if provider supports it."""
        return None
