"""Integration tests for Google OAuth (HTTP mocked)."""

from unittest.mock import patch

from app.integrations.oauth.google_oauth import GoogleOAuthClient


def test_get_authorization_url():
    with patch("app.integrations.oauth.google_oauth.settings") as mock_s:
        mock_s.GOOGLE_CLIENT_ID = "test-client-id"
        client = GoogleOAuthClient()
        url = client.get_authorization_url(
            redirect_uri="https://api.example.com/callback",
            state="state-123",
        )
        assert "accounts.google.com" in url
        assert "client_id=test-client-id" in url
        assert "redirect_uri=" in url
        assert "state=state-123" in url


@patch("app.integrations.oauth.google_oauth.httpx.post")
def test_exchange_code_for_tokens_success(mock_post):
    mock_resp = mock_post.return_value
    mock_resp.raise_for_status = lambda: None
    mock_resp.json.return_value = {
        "access_token": "at",
        "refresh_token": "rt",
        "expires_in": 3600,
    }
    with patch("app.integrations.oauth.google_oauth.settings") as mock_s:
        mock_s.GOOGLE_CLIENT_ID = "cid"
        mock_s.GOOGLE_CLIENT_SECRET = "secret"
        client = GoogleOAuthClient()
        result = client.exchange_code_for_tokens("code", "https://example.com/cb")
    assert result is not None
    assert result.access_token == "at"
    assert result.refresh_token == "rt"
    assert result.expires_at is not None


@patch("app.integrations.oauth.google_oauth.httpx.post")
def test_exchange_code_for_tokens_no_credentials(mock_post):
    with patch("app.integrations.oauth.google_oauth.settings") as mock_s:
        mock_s.GOOGLE_CLIENT_ID = ""
        mock_s.GOOGLE_CLIENT_SECRET = ""
        client = GoogleOAuthClient()
        result = client.exchange_code_for_tokens("code", "https://example.com/cb")
    assert result is None
    mock_post.assert_not_called()
