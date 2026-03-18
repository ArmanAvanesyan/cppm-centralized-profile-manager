"""Provider names and default OAuth scopes for integrations/oauth."""

# Provider identifiers for get_oauth_client()
PROVIDER_GOOGLE = "google"
PROVIDER_MICROSOFT = "microsoft"
PROVIDER_LINKEDIN = "linkedin"
PROVIDER_DROPBOX = "dropbox"

# Default scopes: storage (Drive/OneDrive/Dropbox) vs sign-in only
GOOGLE_SCOPES_STORAGE = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
GOOGLE_SCOPES_SIGNIN = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

MICROSOFT_SCOPES_STORAGE = [
    "offline_access",
    "https://graph.microsoft.com/Files.ReadWrite.All",
]
MICROSOFT_SCOPES_SIGNIN = [
    "openid",
    "profile",
    "User.Read",
]

LINKEDIN_SCOPES_SIGNIN = ["openid", "profile", "email"]

# Dropbox uses token_access_type=offline; no scope list for basic file access
