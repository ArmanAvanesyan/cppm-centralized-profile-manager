"""Unit tests for app.modules.resume_import.repository."""

import uuid

from app.modules.auth.repository import create_user
from app.modules.resume_import.repository import (
    create_extraction,
    create_parsing_result,
    create_resume_upload,
    create_storage_file,
    get_extraction_by_resume,
    get_parsing_result_by_resume,
    get_resume_by_id,
    update_extraction,
    update_parsing_result,
)


def test_create_resume_upload(db_session):
    user = create_user(db_session, "resume_up@example.com")
    row = create_resume_upload(db_session, user.user_id, file_format="pdf", upload_source="api")
    assert row.resume_id is not None
    assert row.user_id == user.user_id
    assert row.file_format == "pdf"


def test_get_resume_by_id(db_session):
    user = create_user(db_session, "resume_get@example.com")
    row = create_resume_upload(db_session, user.user_id)
    found = get_resume_by_id(db_session, row.resume_id)
    assert found is not None
    assert found.resume_id == row.resume_id
    assert get_resume_by_id(db_session, uuid.uuid4()) is None


def test_create_storage_file(db_session):
    user = create_user(db_session, "storage_file@example.com")
    row = create_storage_file(
        db_session, user.user_id, None, "resume.pdf", file_type="pdf", file_size=100
    )
    assert row.file_id is not None
    assert row.file_name == "resume.pdf"


def test_create_extraction(db_session):
    user = create_user(db_session, "extract@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    row = create_extraction(db_session, resume.resume_id, status="pending")
    assert row.extraction_id is not None
    assert row.resume_id == resume.resume_id
    assert row.extraction_status == "pending"


def test_create_parsing_result(db_session):
    user = create_user(db_session, "parse@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    row = create_parsing_result(db_session, resume.resume_id, status="pending")
    assert row.parsing_id is not None
    assert row.resume_id == resume.resume_id


def test_get_extraction_by_resume(db_session):
    user = create_user(db_session, "get_ext@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    create_extraction(db_session, resume.resume_id)
    found = get_extraction_by_resume(db_session, resume.resume_id)
    assert found is not None


def test_get_parsing_result_by_resume(db_session):
    user = create_user(db_session, "get_parse@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    create_parsing_result(db_session, resume.resume_id)
    found = get_parsing_result_by_resume(db_session, resume.resume_id)
    assert found is not None


def test_update_extraction(db_session):
    user = create_user(db_session, "upd_ext@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    ext = create_extraction(db_session, resume.resume_id, status="processing")
    update_extraction(db_session, ext.extraction_id, extracted_text="text", status="completed")
    found = get_extraction_by_resume(db_session, resume.resume_id)
    assert found.extracted_text == "text"
    assert found.extraction_status == "completed"


def test_update_parsing_result(db_session):
    user = create_user(db_session, "upd_parse@example.com")
    resume = create_resume_upload(db_session, user.user_id)
    pr = create_parsing_result(db_session, resume.resume_id)
    update_parsing_result(
        db_session, pr.parsing_id, parsed_experience=[], parsed_skills=[], status="completed"
    )
    found = get_parsing_result_by_resume(db_session, resume.resume_id)
    assert found.parsing_status == "completed"
