"""API tests for linkedin_import router."""

from io import BytesIO

from app.database.models import User
from app.modules.linkedin_import.repository import create_linkedin_import


def test_linkedin_import_upload(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="li_upload_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post(
        "/api/v1/linkedin/import",
        files={"file": ("linkedin.pdf", BytesIO(b"content"), "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "import_id" in data
    assert data["status"] == "uploaded"


def test_linkedin_parse(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="li_parse_api@example.com")
    db_session.add(user)
    db_session.commit()
    imp = create_linkedin_import(db_session, auth_user_id)
    r = client_with_auth.post(f"/api/v1/linkedin/import/{imp.import_id}/parse")
    assert r.status_code == 202
    assert r.json()["status"] == "processing"


def test_linkedin_parse_not_found(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="li_nf@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post("/api/v1/linkedin/import/00000000-0000-0000-0000-000000000099/parse")
    assert r.status_code == 404
