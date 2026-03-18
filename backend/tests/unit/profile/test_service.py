"""Unit tests for app.modules.profile.service."""

from app.modules.auth.repository import create_user
from app.modules.profile.service import get_profile, merge_into_profile, update_profile


def test_get_profile(db_session):
    user = create_user(db_session, "profile_get@example.com")
    data = get_profile(db_session, user.user_id)
    assert "basics" in data
    assert "experience" in data
    assert "skills" in data
    assert data["experience"] == []
    assert data["skills"] == []


def test_update_profile(db_session):
    user = create_user(db_session, "profile_upd@example.com")
    data = {"basics": {"name": "Test"}, "experience": [], "skills": []}
    result = update_profile(db_session, user.user_id, data)
    assert result == data


def test_merge_into_profile(db_session):
    import uuid

    user = create_user(db_session, "profile_merge@example.com")
    source_id = uuid.uuid4()
    ok = merge_into_profile(db_session, user.user_id, "resume", source_id)
    assert ok is True
    from app.database.models import ProfileMergeOperation

    row = (
        db_session.query(ProfileMergeOperation)
        .filter(
            ProfileMergeOperation.user_id == user.user_id,
            ProfileMergeOperation.source_id == source_id,
        )
        .first()
    )
    assert row is not None
    assert row.merge_status == "completed"
