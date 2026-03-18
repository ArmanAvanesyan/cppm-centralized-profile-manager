import uuid

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LinkedInImport(Base):
    __tablename__ = "linkedin_imports"

    import_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_files.file_id")
    )
    import_type: Mapped[str | None] = mapped_column(String(50))
    import_status: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )


class LinkedInParsedData(Base):
    __tablename__ = "linkedin_parsed_data"

    parsed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    import_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("linkedin_imports.import_id", ondelete="CASCADE"),
        nullable=False,
    )
    parsed_experience: Mapped[dict | list | None] = mapped_column(JSONB)
    parsed_education: Mapped[dict | list | None] = mapped_column(JSONB)
    parsed_skills: Mapped[dict | list | None] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )
