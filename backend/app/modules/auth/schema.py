from pydantic import BaseModel, EmailStr


class EmailSignupRequest(BaseModel):
    email: EmailStr


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    otp: str


class GoogleTokenRequest(BaseModel):
    id_token: str


class MicrosoftTokenRequest(BaseModel):
    access_token: str


class LinkedInTokenRequest(BaseModel):
    access_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class CurrentUserResponse(BaseModel):
    user_id: str
    email: str
    providers: list[str]

    class Config:
        from_attributes = True
