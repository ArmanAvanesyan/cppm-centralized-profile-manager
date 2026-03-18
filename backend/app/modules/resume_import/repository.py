import uuid

from sqlalchemy.orm import Session

from app.database.models import ResumeParsingResult, ResumeTextExtraction, ResumeUpload, StorageFile


def create_resume_upload(
    db: Session,
    user_id: uuid.UUID,
    file_id: uuid.UUID | None = None,
    file_format: str | None = None,
    upload_source: str | None = None,
) -> ResumeUpload:
    row = ResumeUpload(
        user_id=user_id,
        file_id=file_id,
        file_format=file_format,
        upload_source=upload_source,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_resume_by_id(db: Session, resume_id: uuid.UUID) -> ResumeUpload | None:
    return db.get(ResumeUpload, resume_id)


def create_storage_file(
    db: Session,
    user_id: uuid.UUID,
    account_id: uuid.UUID | None,
    file_name: str,
    file_type: str | None = None,
    file_size: int | None = None,
) -> StorageFile:
    row = StorageFile(
        user_id=user_id,
        account_id=account_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_extraction(
    db: Session, resume_id: uuid.UUID, status: str = "pending"
) -> ResumeTextExtraction:
    row = ResumeTextExtraction(resume_id=resume_id, extraction_status=status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_parsing_result(
    db: Session, resume_id: uuid.UUID, status: str = "pending"
) -> ResumeParsingResult:
    row = ResumeParsingResult(resume_id=resume_id, parsing_status=status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_extraction_by_resume(db: Session, resume_id: uuid.UUID) -> ResumeTextExtraction | None:
    return (
        db.query(ResumeTextExtraction).filter(ResumeTextExtraction.resume_id == resume_id).first()
    )


def get_parsing_result_by_resume(db: Session, resume_id: uuid.UUID) -> ResumeParsingResult | None:
    return db.query(ResumeParsingResult).filter(ResumeParsingResult.resume_id == resume_id).first()


def update_extraction(
    db: Session,
    extraction_id: uuid.UUID,
    extracted_text: str | None = None,
    status: str | None = None,
) -> None:
    row = db.get(ResumeTextExtraction, extraction_id)
    if row:
        if extracted_text is not None:
            row.extracted_text = extracted_text
        if status is not None:
            row.extraction_status = status
        db.commit()


def update_parsing_result(
    db: Session,
    parsing_id: uuid.UUID,
    parsed_experience: list | dict | None = None,
    parsed_skills: list | dict | None = None,
    status: str | None = None,
) -> None:
    row = db.get(ResumeParsingResult, parsing_id)
    if row:
        if parsed_experience is not None:
            row.parsed_experience = parsed_experience
        if parsed_skills is not None:
            row.parsed_skills = parsed_skills
        if status is not None:
            row.parsing_status = status
        db.commit()
