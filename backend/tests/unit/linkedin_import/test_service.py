"""Unit tests for app.modules.linkedin_import.service."""

from io import BytesIO

from app.modules.auth.repository import create_user
from app.modules.linkedin_import.repository import create_linkedin_import
from app.modules.linkedin_import.service import start_parse, upload_import
from fastapi import UploadFile


def test_upload_import(db_session):
    user = create_user(db_session, "li_upload_svc@example.com")
    f = UploadFile(filename="linkedin.pdf", file=BytesIO(b"data"))
    import_id, status = upload_import(db_session, user.user_id, f)
    assert import_id is not None
    assert status == "uploaded"


def test_start_parse(db_session):
    user = create_user(db_session, "li_parse_svc@example.com")
    imp = create_linkedin_import(db_session, user.user_id)
    job_id = start_parse(db_session, imp.import_id, user.user_id)
    assert job_id is not None


def test_start_parse_wrong_user(db_session):
    user1 = create_user(db_session, "li_u1@example.com")
    user2 = create_user(db_session, "li_u2@example.com")
    imp = create_linkedin_import(db_session, user1.user_id)
    assert start_parse(db_session, imp.import_id, user2.user_id) is None
