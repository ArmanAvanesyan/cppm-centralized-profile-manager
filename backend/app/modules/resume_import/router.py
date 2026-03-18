from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.resume_import import schema
from app.modules.resume_import.service import start_extract, start_parse, upload_resume

router = APIRouter()


@router.post("/upload", response_model=schema.ResumeUploadResponse)
def resume_upload(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume_id, st = upload_resume(db, current_user.user_id, file)
    return schema.ResumeUploadResponse(resume_id=str(resume_id), status=st)


@router.post(
    "/{resume_id}/extract",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schema.JobAcceptedResponse,
)
def extract_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from uuid import UUID

    try:
        rid = UUID(resume_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid resume_id"
        ) from e
    job_id = start_extract(db, rid, current_user.user_id)
    if not job_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return schema.JobAcceptedResponse(job_id=str(job_id), status="processing")


@router.post(
    "/{resume_id}/parse",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schema.JobAcceptedResponse,
)
def parse_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from uuid import UUID

    try:
        rid = UUID(resume_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid resume_id"
        ) from e
    job_id = start_parse(db, rid, current_user.user_id)
    if not job_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return schema.JobAcceptedResponse(job_id=str(job_id), status="processing")
