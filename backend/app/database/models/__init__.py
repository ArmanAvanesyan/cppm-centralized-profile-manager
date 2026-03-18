# Import all models so Alembic can see Base.metadata
from app.database.models.user import User
from app.database.models.auth import AuthProvider, EmailOtp, Session
from app.database.models.cloud import (
    CloudProvider,
    UserCloudAccount,
    StorageFolder,
    StorageFile,
)
from app.database.models.resume import (
    ResumeUpload,
    ResumeTextExtraction,
    ResumeParsingResult,
)
from app.database.models.linkedin import LinkedInImport, LinkedInParsedData
from app.database.models.profile_merge import ProfileMergeOperation
from app.database.models.encryption import EncryptionKey, EncryptedToken

__all__ = [
    "User",
    "AuthProvider",
    "EmailOtp",
    "Session",
    "CloudProvider",
    "UserCloudAccount",
    "StorageFolder",
    "StorageFile",
    "ResumeUpload",
    "ResumeTextExtraction",
    "ResumeParsingResult",
    "LinkedInImport",
    "LinkedInParsedData",
    "ProfileMergeOperation",
    "EncryptionKey",
    "EncryptedToken",
]
