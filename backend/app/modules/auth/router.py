from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.database.models import User
from app.modules.auth import schema
from app.modules.auth.service import (
    email_signup,
    email_verify,
    get_me,
    google_login,
    linkedin_login,
    logout,
    microsoft_login,
    refresh_tokens,
)

router = APIRouter()


@router.post("/email/signup", response_model=schema.MessageResponse)
def signup(
    body: schema.EmailSignupRequest,
    db: Session = Depends(get_db),
):
    email_signup(db, body.email)
    return schema.MessageResponse(message="OTP sent")


@router.post("/email/verify", response_model=schema.TokenResponse)
def verify(
    body: schema.EmailVerifyRequest,
    db: Session = Depends(get_db),
):
    tokens = email_verify(db, body.email, body.otp)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )
    return schema.TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/google", response_model=schema.TokenResponse)
def google(
    body: schema.GoogleTokenRequest,
    db: Session = Depends(get_db),
):
    tokens = google_login(db, body.id_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    return schema.TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/microsoft", response_model=schema.TokenResponse)
def microsoft(
    body: schema.MicrosoftTokenRequest,
    db: Session = Depends(get_db),
):
    tokens = microsoft_login(db, body.access_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Microsoft token",
        )
    return schema.TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/linkedin", response_model=schema.TokenResponse)
def linkedin(
    body: schema.LinkedInTokenRequest,
    db: Session = Depends(get_db),
):
    tokens = linkedin_login(db, body.access_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LinkedIn token",
        )
    return schema.TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.get("/me", response_model=schema.CurrentUserResponse)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return schema.CurrentUserResponse(**get_me(db, current_user))


@router.post("/refresh", response_model=schema.TokenResponse)
def refresh(
    body: schema.RefreshRequest,
    db: Session = Depends(get_db),
):
    tokens = refresh_tokens(db, body.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return schema.TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_route(
    body: schema.RefreshRequest | None = None,
    db: Session = Depends(get_db),
):
    refresh_token = body.refresh_token if body else None
    logout(db, refresh_token)
