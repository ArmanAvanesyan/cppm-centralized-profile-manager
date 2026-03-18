from pydantic import BaseModel


class ProfileMergeRequest(BaseModel):
    source_type: str  # "resume" | "linkedin"
    source_id: str  # uuid


class ProfileUpdateRequest(BaseModel):
    basics: dict | None = None
    experience: list | None = None
    skills: list | None = None
