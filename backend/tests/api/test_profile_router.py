"""API tests for profile router."""

from app.database.models import User


def test_profile_get(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="profile_api@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.get("/api/v1/profile")
    assert r.status_code == 200
    data = r.json()
    assert "basics" in data
    assert "experience" in data
    assert "skills" in data


def test_profile_put(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="profile_put@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.put(
        "/api/v1/profile",
        json={"basics": {"name": "Alice"}, "experience": None, "skills": None},
    )
    assert r.status_code == 200
    assert r.json()["basics"]["name"] == "Alice"


def test_profile_merge(client_with_auth, db_session, auth_user_id):
    import uuid

    user = User(user_id=auth_user_id, email="profile_merge_api@example.com")
    db_session.add(user)
    db_session.commit()
    source_id = str(uuid.uuid4())
    r = client_with_auth.post(
        "/api/v1/profile/merge",
        json={"source_type": "resume", "source_id": source_id},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "merged"


def test_profile_merge_invalid_source_type(client_with_auth, db_session, auth_user_id):
    user = User(user_id=auth_user_id, email="profile_merge_inv@example.com")
    db_session.add(user)
    db_session.commit()
    r = client_with_auth.post(
        "/api/v1/profile/merge",
        json={"source_type": "invalid", "source_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert r.status_code == 400
