from pydantic import BaseModel


class LinkedInImportResponse(BaseModel):
    import_id: str
    status: str


class JobAcceptedResponse(BaseModel):
    job_id: str
    status: str
