from datetime import datetime

from pydantic import BaseModel


class ConnectResponse(BaseModel):
    auth_url: str


class CloudAccountResponse(BaseModel):
    provider: str
    connected_at: datetime

    class Config:
        from_attributes = True
