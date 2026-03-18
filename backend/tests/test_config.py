"""Tests for app.core.config."""
import os

import pytest

from app.core.config import Settings


def test_settings_defaults():
    """Defaults match expected values when env is not set."""
    # Use a fresh Settings instance; avoid mutating global settings
    s = Settings(
        _env_file=None,
        DATABASE_URL="postgresql://localhost:5432/cppm",
    )
    assert s.DATABASE_URL == "postgresql://localhost:5432/cppm"
    assert s.JWT_SECRET == "change-me-in-production"
    assert s.JWT_ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert s.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert s.OTP_SECRET == "change-me-otp"
    assert s.OTP_EXPIRE_MINUTES == 10
    assert s.STORAGE_CALLBACK_BASE_URL == "http://localhost:8000/api/v1/storage/callback"


def test_settings_from_env(monkeypatch):
    """Settings load from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:5432/db")
    monkeypatch.setenv("JWT_SECRET", "secret-from-env")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    # Create new instance so it reads env
    s = Settings(_env_file=None)
    assert s.DATABASE_URL == "postgresql://test:5432/db"
    assert s.JWT_SECRET == "secret-from-env"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 60
