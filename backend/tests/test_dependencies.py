"""Tests for app.core.dependencies."""
import uuid

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.dependencies import get_current_user, get_current_user_id
from app.database.models import User


def test_get_current_user_id_no_credentials():
    """Missing credentials raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(credentials=None)
    assert exc_info.value.status_code == 401
    assert "Not authenticated" in exc_info.value.detail


def test_get_current_user_id_invalid_token():
    """Invalid or malformed JWT raises 401."""
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-jwt")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(credentials=creds)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_id_token_without_sub():
    """Token without 'sub' claim raises 401."""
    from app.core.config import settings
    from datetime import datetime, timedelta, timezone
    from jose import jwt

    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(
        payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(credentials=creds)
    assert exc_info.value.status_code == 401
    assert "Invalid token payload" in exc_info.value.detail


def test_get_current_user_id_valid_token():
    """Valid JWT with 'sub' returns UUID."""
    from tests.conftest import make_token

    user_id = uuid.uuid4()
    token = make_token(user_id)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    result = get_current_user_id(credentials=creds)
    assert result == user_id


def test_get_current_user_not_found(db_session):
    """User not in DB raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=db_session, user_id=uuid.uuid4())
    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail


def test_get_current_user_found(db_session):
    """User in DB is returned."""
    user = User(email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    result = get_current_user(db=db_session, user_id=user.user_id)
    assert result is user
    assert result.email == "test@example.com"
