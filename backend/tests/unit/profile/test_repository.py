"""Unit tests for app.modules.profile.repository."""

import uuid

from app.modules.auth.repository import create_user
from app.modules.profile.repository import create_merge_operation


def test_create_merge_operation(db_session):
    user = create_user(db_session, "merge@example.com")
    source_id = uuid.uuid4()
    row = create_merge_operation(
        db_session,
        user_id=user.user_id,
        source_type="resume",
        source_id=source_id,
        merge_status="completed",
    )
    assert row.user_id == user.user_id
    assert row.source_type == "resume"
    assert row.source_id == source_id
    assert row.merge_status == "completed"
