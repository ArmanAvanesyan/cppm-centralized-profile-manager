import uuid

from sqlalchemy.orm import Session

from app.modules.profile.repository import create_merge_operation


def get_profile(_db: Session, _user_id: uuid.UUID) -> dict:
    """Read profile.json from user's cloud. Stub: return empty profile."""
    # TODO: get user's default cloud account, use integration client to read profile.json
    return {"basics": {}, "experience": [], "skills": []}


def update_profile(_db: Session, _user_id: uuid.UUID, data: dict) -> dict:
    """Write profile.json to user's cloud. Stub: return same data."""
    # TODO: get user's default cloud account, use integration client to write profile.json
    return data


def merge_into_profile(
    db: Session, user_id: uuid.UUID, source_type: str, source_id: uuid.UUID
) -> bool:
    """Merge parsed data from resume or linkedin into profile.json. Stub."""
    # TODO: load resume_parsing_results or linkedin_parsed_data by source_id,
    # get current profile from cloud, merge, write back, create profile_merge_operations
    create_merge_operation(db, user_id, source_type, source_id, "completed")
    return True
