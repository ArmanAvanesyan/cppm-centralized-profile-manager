from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.linkedin_import import schema
from app.modules.linkedin_import.service import start_parse, upload_import

router = APIRouter()


@router.post("/import", response_model=schema.LinkedInImportResponse)
def linkedin_import_upload(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import_id, st = upload_import(db, current_user.user_id, file)
    return schema.LinkedInImportResponse(import_id=str(import_id), status=st)


@router.post("/import/{import_id}/parse", status_code=status.HTTP_202_ACCEPTED, response_model=schema.JobAcceptedResponse)
def linkedin_parse(
    import_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        iid = UUID(import_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid import_id")
    job_id = start_parse(db, iid, current_user.user_id)
    if not job_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import not found")
    return schema.JobAcceptedResponse(job_id=str(job_id), status="processing")
