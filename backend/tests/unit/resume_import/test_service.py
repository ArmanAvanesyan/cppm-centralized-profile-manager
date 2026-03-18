"""Unit tests for app.modules.resume_import.service."""

from io import BytesIO

from app.modules.auth.repository import create_user
from app.modules.resume_import.repository import create_resume_upload
from app.modules.resume_import.service import start_extract, start_parse, upload_resume
from fastapi import UploadFile


def test_upload_resume(db_session):
    user = create_user(db_session, "upload_svc@example.com")
    f = UploadFile(filename="cv.pdf", file=BytesIO(b"pdf content"))
    resume_id, status = upload_resume(db_session, user.user_id, f)
    assert resume_id is not None
    assert status == "uploaded"


def test_start_extract(db_session):
    user = create_user(db_session, "extract_svc@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    job_id = start_extract(db_session, resume.resume_id, user.user_id)
    assert job_id is not None


def test_start_extract_wrong_user(db_session):
    user1 = create_user(db_session, "u1@example.com")
    user2 = create_user(db_session, "u2@example.com")
    resume = create_resume_upload(db_session, user1.user_id)
    assert start_extract(db_session, resume.resume_id, user2.user_id) is None


def test_start_parse(db_session):
    user = create_user(db_session, "parse_svc@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    job_id = start_parse(db_session, resume.resume_id, user.user_id)
    assert job_id is not None


def test_start_parse_resume_not_found(db_session):
    user = create_user(db_session, "parse_nf@example.com")
    import uuid

    assert start_parse(db_session, uuid.uuid4(), user.user_id) is None
