"""API tests for resume_import router."""

from io import BytesIO

from app.database.models import User
from app.modules.resume_import.repository import create_resume_upload


def test_resume_upload(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="resume_upload_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post(
        "/api/v1/resume/upload",
        files={"file": ("resume.pdf", BytesIO(b"content"), "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "resume_id" in data
    assert data["status"] == "uploaded"


def test_resume_extract(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="resume_extract_api@example.com")
    db_session.add(user)
    db_session.commit()
    resume = create_resume_upload(db_session, auth_user_id)
    r = client_with_auth.post(f"/api/v1/resume/{resume.resume_id}/extract")
    assert r.status_code == 202
    assert "job_id" in r.json()


def test_resume_extract_not_found(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="resume_nf@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post("/api/v1/resume/00000000-0000-0000-0000-000000000099/extract")
    assert r.status_code == 404


def test_resume_parse(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="resume_parse_api@example.com")
    db_session.add(user)
    db_session.commit()
    resume = create_resume_upload(db_session, auth_user_id)
    r = client_with_auth.post(f"/api/v1/resume/{resume.resume_id}/parse")
    assert r.status_code == 202
    assert r.json()["status"] == "processing"
