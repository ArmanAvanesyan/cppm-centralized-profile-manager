from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.profile import schema
from app.modules.profile.service import get_profile, merge_into_profile, update_profile

router = APIRouter()


@router.get("")
def profile_get(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_profile(db, current_user.user_id)


@router.put("")
def profile_put(
    body: schema.ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = {}
    if body.basics is not None:
        data["basics"] = body.basics
    if body.experience is not None:
        data["experience"] = body.experience
    if body.skills is not None:
        data["skills"] = body.skills
    return update_profile(db, current_user.user_id, data)


@router.post("/merge")
def profile_merge(
    body: schema.ProfileMergeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        source_id = UUID(body.source_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid source_id"
        ) from e
    if body.source_type not in ("resume", "linkedin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_type must be 'resume' or 'linkedin'",
        )
    ok = merge_into_profile(db, current_user.user_id, body.source_type, source_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Merge failed")
    return {"status": "merged"}
