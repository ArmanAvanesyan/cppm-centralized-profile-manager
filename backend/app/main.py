from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.modules.auth as auth
import app.modules.cloud_storage as cloud_storage
import app.modules.resume_import as resume_import
import app.modules.linkedin_import as linkedin_import
import app.modules.profile as profile
import app.modules.encryption as encryption

app = FastAPI(
    title="CPPM API",
    description="Centralized Professional Profile Manager - Backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(cloud_storage.router, prefix="/api/v1/storage", tags=["storage"])
app.include_router(resume_import.router, prefix="/api/v1/resume", tags=["resume"])
app.include_router(linkedin_import.router, prefix="/api/v1/linkedin", tags=["linkedin"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(encryption.router, prefix="/api/v1/encryption", tags=["encryption"])


@app.get("/health")
def health():
    return {"status": "ok"}
