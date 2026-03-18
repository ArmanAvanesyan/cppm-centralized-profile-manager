from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/cppm"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP (email auth)
    OTP_SECRET: str = "change-me-otp"
    OTP_EXPIRE_MINUTES: int = 10

    # Google OAuth (auth + drive)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"

    # Dropbox OAuth (cloud storage)
    DROPBOX_CLIENT_ID: str = ""
    DROPBOX_CLIENT_SECRET: str = ""

    # LinkedIn OAuth (Sign in with LinkedIn / OpenID Connect) (Sign in with LinkedIn / OpenID Connect)
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""

    # Cloud storage OAuth callback base (e.g. https://api.example.com/api/v1/storage/callback)
    STORAGE_CALLBACK_BASE_URL: str = "http://localhost:8000/api/v1/storage/callback"


settings = Settings()
