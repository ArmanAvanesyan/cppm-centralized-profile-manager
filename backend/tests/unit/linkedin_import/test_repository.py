"""Unit tests for app.modules.linkedin_import.repository."""

import uuid

from app.modules.auth.repository import create_user
from app.modules.linkedin_import.repository import (
    create_linkedin_import,
    create_parsed_data,
    get_import_by_id,
)


def test_create_linkedin_import(db_session):
    user = create_user(db_session, "li_imp@example.com")
    row = create_linkedin_import(
        db_session, user.user_id, import_type="pdf", import_status="uploaded"
    )
    assert row.import_id is not None
    assert row.user_id == user.user_id
    assert row.import_status == "uploaded"


def test_get_import_by_id(db_session):
    user = create_user(db_session, "li_get@example.com")
    row = create_linkedin_import(db_session, user.user_id)
    found = get_import_by_id(db_session, row.import_id)
    assert found is not None
    assert get_import_by_id(db_session, uuid.uuid4()) is None


def test_create_parsed_data(db_session):
    user = create_user(db_session, "li_parsed@example.com")
    imp = create_linkedin_import(db_session, user.user_id)
    row = create_parsed_data(db_session, imp.import_id, parsed_experience=[], parsed_skills=[])
    assert row.parsed_id is not None
    assert row.import_id == imp.import_id
