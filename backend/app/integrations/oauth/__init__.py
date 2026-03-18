"""OAuth2 integrations: Google, Microsoft, LinkedIn, Dropbox (auth URL + token exchange only)."""

from app.integrations.oauth.base_oauth import BaseOAuthClient, OAuthTokenResult
from app.integrations.oauth.constants import (
    PROVIDER_DROPBOX,
    PROVIDER_GOOGLE,
    PROVIDER_LINKEDIN,
    PROVIDER_MICROSOFT,
)
from app.integrations.oauth.dropbox_oauth import DropboxOAuthClient
from app.integrations.oauth.google_oauth import GoogleOAuthClient
from app.integrations.oauth.linkedin_oauth import LinkedInOAuthClient
from app.integrations.oauth.microsoft_oauth import MicrosoftOAuthClient

_oauth_clients: dict[str, BaseOAuthClient] = {
    PROVIDER_GOOGLE: GoogleOAuthClient(),
    PROVIDER_MICROSOFT: MicrosoftOAuthClient(),
    PROVIDER_LINKEDIN: LinkedInOAuthClient(),
    PROVIDER_DROPBOX: DropboxOAuthClient(),
}


def get_oauth_client(provider: str) -> BaseOAuthClient:
    """Return the OAuth client for the given provider. Raises KeyError if unknown."""
    key = provider.lower()
    if key not in _oauth_clients:
        raise KeyError(f"Unknown OAuth provider: {provider}")
    return _oauth_clients[key]


__all__ = [
    "BaseOAuthClient",
    "OAuthTokenResult",
    "get_oauth_client",
    "GoogleOAuthClient",
    "MicrosoftOAuthClient",
    "LinkedInOAuthClient",
    "DropboxOAuthClient",
]
