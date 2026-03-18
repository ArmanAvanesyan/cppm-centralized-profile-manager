from pydantic import BaseModel


class EncryptionInitRequest(BaseModel):
    password: str


class EncryptionStatusResponse(BaseModel):
    initialized: bool
    key_version: int | None = None
