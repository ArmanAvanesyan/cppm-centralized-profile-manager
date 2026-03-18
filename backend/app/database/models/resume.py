import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ResumeUpload(Base):
    __tablename__ = "resume_uploads"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_files.file_id")
    )
    file_format: Mapped[str | None] = mapped_column(String(20))
    upload_source: Mapped[str | None] = mapped_column(String(50))
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")


class ResumeTextExtraction(Base):
    __tablename__ = "resume_text_extraction"

    extraction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_uploads.resume_id", ondelete="CASCADE"),
        nullable=False,
    )
    extracted_text: Mapped[str | None] = mapped_column(Text)
    extraction_status: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")


class ResumeParsingResult(Base):
    __tablename__ = "resume_parsing_results"

    parsing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_uploads.resume_id", ondelete="CASCADE"),
        nullable=False,
    )
    parsed_experience: Mapped[dict | list | None] = mapped_column(JSONB)
    parsed_skills: Mapped[dict | list | None] = mapped_column(JSONB)
    parsing_status: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")
