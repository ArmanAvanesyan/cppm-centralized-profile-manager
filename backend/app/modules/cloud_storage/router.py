import contextlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.cloud_storage import schema
from app.modules.cloud_storage.service import get_connect_url, handle_callback, list_accounts

router = APIRouter()

VALID_PROVIDERS = {"google", "dropbox", "onedrive"}


@router.post("/connect/{provider}", response_model=schema.ConnectResponse)
def connect(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if provider.lower() not in VALID_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider must be one of: {', '.join(VALID_PROVIDERS)}",
        )
    try:
        auth_url = get_connect_url(db, provider, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schema.ConnectResponse(auth_url=auth_url)


@router.get("/callback/{provider}")
def callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    if provider.lower() not in VALID_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider must be one of: {', '.join(VALID_PROVIDERS)}",
        )
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code")
    user_id: uuid.UUID | None = None
    if state:
        with contextlib.suppress(ValueError, TypeError):
            user_id = uuid.UUID(state)
    ok = handle_callback(db, provider, code, state, user_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Callback failed",
        )
    return {"status": "connected"}


@router.get("/accounts", response_model=list[schema.CloudAccountResponse])
def list_cloud_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = list_accounts(db, current_user.user_id)
    return [schema.CloudAccountResponse(**x) for x in items]
