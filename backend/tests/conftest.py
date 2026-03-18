"""Shared pytest fixtures: test DB, TestClient, auth overrides."""
import os
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.dependencies import get_db, get_current_user, get_current_user_id
from app.database.base import Base
from app.main import app

# Import models so Base.metadata has all tables
import app.database.models  # noqa: F401

# Use TEST_DATABASE_URL if set, else DATABASE_URL (PostgreSQL). Rollback per test for isolation.
_TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", settings.DATABASE_URL)
_TEST_ENGINE = create_engine(
    _TEST_DATABASE_URL,
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_TEST_ENGINE,
)


def _create_tables() -> None:
    Base.metadata.create_all(bind=_TEST_ENGINE)
    # Seed cloud_providers so cloud_storage tests can resolve provider names
    with _TEST_ENGINE.connect() as conn:
        conn.execute(text(
            "INSERT INTO cloud_providers (name) VALUES ('google_drive'), ('dropbox'), ('onedrive')"
        ))
        conn.commit()


def _db_available() -> bool:
    try:
        with _TEST_ENGINE.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def db_engine():
    if not _db_available():
        pytest.skip(
            "Test database not available. Set TEST_DATABASE_URL (or DATABASE_URL) to a running PostgreSQL."
        )
    _create_tables()
    yield _TEST_ENGINE
    Base.metadata.drop_all(bind=_TEST_ENGINE)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a DB session that rolls back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session):
    """FastAPI TestClient with get_db overridden to use test session."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_user_id() -> uuid.UUID:
    """Default user_id for auth tests (use with auth_token and override_get_current_user)."""
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


def make_token(user_id: uuid.UUID) -> str:
    """Create a valid access token for the given user_id."""
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


@pytest.fixture
def auth_token(auth_user_id: uuid.UUID) -> str:
    """Valid JWT for auth_user_id."""
    return make_token(auth_user_id)


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Headers with Bearer token for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def client_with_auth(db_session: Session, auth_user_id: uuid.UUID):
    """
    TestClient with get_db and get_current_user_id overridden.
    Requires a User with auth_user_id to exist in db_session (caller must create it).
    """
    from app.database.models import User

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass


    def override_get_current_user_id() -> uuid.UUID:
            return auth_user_id

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user_id, None)

