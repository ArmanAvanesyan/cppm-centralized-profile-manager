from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.encryption import schema
from app.modules.encryption.service import get_status, init_encryption, rotate_key

router = APIRouter()


@router.post("/init")
def encryption_init(
    body: schema.EncryptionInitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    init_encryption(db, current_user.user_id, body.password)
    return {"status": "initialized"}


@router.post("/rotate")
def encryption_rotate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ok = rotate_key(db, current_user.user_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Encryption not initialized")
    return {"status": "rotated"}


@router.get("/status", response_model=schema.EncryptionStatusResponse)
def encryption_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return schema.EncryptionStatusResponse(**get_status(db, current_user.user_id))
