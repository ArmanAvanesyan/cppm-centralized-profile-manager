import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.modules.resume_import.repository import (
    create_extraction,
    create_parsing_result,
    create_resume_upload,
    create_storage_file,
    get_resume_by_id,
)


def upload_resume(
    db: Session, user_id: uuid.UUID, file: UploadFile
) -> tuple[uuid.UUID, str]:
    """Store file metadata and create resume_upload. Returns (resume_id, status)."""
    # For MVP: don't upload to cloud; create storage_file with name/size only
    content = file.file.read()
    file_size = len(content)
    file_type = file.filename.split(".")[-1] if file.filename else None
    storage_file = create_storage_file(
        db, user_id, account_id=None, file_name=file.filename or "resume", file_type=file_type, file_size=file_size
    )
    resume = create_resume_upload(
        db, user_id=user_id, file_id=storage_file.file_id, file_format=file_type, upload_source="api"
    )
    return resume.resume_id, "uploaded"


def start_extract(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID | None:
    """Create extraction job (pending), return job_id (extraction_id). 202 flow."""
    resume = get_resume_by_id(db, resume_id)
    if not resume or resume.user_id != user_id:
        return None
    ext = create_extraction(db, resume_id, status="processing")
    # Stub: sync run; in production enqueue worker
    # update_extraction(db, ext.extraction_id, extracted_text="...", status="completed")
    return ext.extraction_id


def start_parse(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID | None:
    """Create parsing job (pending), return job_id (parsing_id). 202 flow."""
    resume = get_resume_by_id(db, resume_id)
    if not resume or resume.user_id != user_id:
        return None
    pr = create_parsing_result(db, resume_id, status="processing")
    return pr.parsing_id
