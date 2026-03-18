import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.modules.linkedin_import.repository import (
    create_linkedin_import,
    create_storage_file,
    get_import_by_id,
)


def upload_import(db: Session, user_id: uuid.UUID, file: UploadFile) -> tuple[uuid.UUID, str]:
    content = file.file.read()
    file_size = len(content)
    file_type = file.filename.split(".")[-1] if file.filename else None
    storage_file = create_storage_file(
        db, user_id, account_id=None, file_name=file.filename or "linkedin", file_type=file_type, file_size=file_size
    )
    imp = create_linkedin_import(
        db, user_id=user_id, file_id=storage_file.file_id, import_type=file_type, import_status="uploaded"
    )
    return imp.import_id, "uploaded"


def start_parse(db: Session, import_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID | None:
    imp = get_import_by_id(db, import_id)
    if not imp or imp.user_id != user_id:
        return None
    from app.modules.linkedin_import.repository import create_parsed_data
    row = create_parsed_data(db, import_id)
    return row.parsed_id
