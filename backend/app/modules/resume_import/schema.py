from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    resume_id: str
    status: str


class JobAcceptedResponse(BaseModel):
    job_id: str
    status: str


class ResumeParseResultResponse(BaseModel):
    experience: list
    skills: list
