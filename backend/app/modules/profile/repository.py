import uuid

from sqlalchemy.orm import Session

from app.database.models import ProfileMergeOperation


def create_merge_operation(
    db: Session,
    user_id: uuid.UUID,
    source_type: str,
    source_id: uuid.UUID,
    merge_status: str = "completed",
) -> ProfileMergeOperation:
    row = ProfileMergeOperation(
        user_id=user_id,
        source_type=source_type,
        source_id=source_id,
        merge_status=merge_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
