import uuid

from sqlalchemy.orm import Session

from app.database.models import LinkedInImport, LinkedInParsedData, StorageFile


def create_linkedin_import(
    db: Session,
    user_id: uuid.UUID,
    file_id: uuid.UUID | None = None,
    import_type: str | None = None,
    import_status: str = "uploaded",
) -> LinkedInImport:
    row = LinkedInImport(
        user_id=user_id,
        file_id=file_id,
        import_type=import_type,
        import_status=import_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_import_by_id(db: Session, import_id: uuid.UUID) -> LinkedInImport | None:
    return db.get(LinkedInImport, import_id)


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


def create_parsed_data(
    db: Session,
    import_id: uuid.UUID,
    parsed_experience: list | dict | None = None,
    parsed_education: list | dict | None = None,
    parsed_skills: list | dict | None = None,
) -> LinkedInParsedData:
    row = LinkedInParsedData(
        import_id=import_id,
        parsed_experience=parsed_experience,
        parsed_education=parsed_education,
        parsed_skills=parsed_skills,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
