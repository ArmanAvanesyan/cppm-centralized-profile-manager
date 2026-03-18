"""Initial schema: all MVP tables + seed cloud_providers

Revision ID: 001_initial
Revises:
Create Date: Initial

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("email_verified", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "cloud_providers",
        sa.Column("provider_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("provider_id"),
    )
    op.create_index("ix_cloud_providers_name", "cloud_providers", ["name"], unique=True)

    op.create_table(
        "auth_providers",
        sa.Column("provider_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_user_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_auth_provider_provider_user"),
    )

    op.create_table(
        "email_otps",
        sa.Column("otp_id", sa.UUID(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("otp_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "sessions",
        sa.Column("session_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "user_cloud_accounts",
        sa.Column("account_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("cloud_providers.provider_id"), nullable=False),
        sa.Column("external_account_id", sa.String(255)),
        sa.Column("access_token_encrypted", sa.Text()),
        sa.Column("refresh_token_encrypted", sa.Text()),
        sa.Column("token_expires_at", sa.DateTime(timezone=True)),
        sa.Column("connected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "storage_folders",
        sa.Column("folder_id", sa.UUID(), primary_key=True),
        sa.Column("account_id", sa.UUID(), sa.ForeignKey("user_cloud_accounts.account_id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_folder_id", sa.String(255)),
        sa.Column("folder_path", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "storage_files",
        sa.Column("file_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.UUID(), sa.ForeignKey("user_cloud_accounts.account_id")),
        sa.Column("provider_file_id", sa.String(255)),
        sa.Column("file_name", sa.String(255)),
        sa.Column("file_type", sa.String(50)),
        sa.Column("file_size", sa.BigInteger()),
        sa.Column("checksum", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "resume_uploads",
        sa.Column("resume_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_id", sa.UUID(), sa.ForeignKey("storage_files.file_id")),
        sa.Column("file_format", sa.String(20)),
        sa.Column("upload_source", sa.String(50)),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "resume_text_extraction",
        sa.Column("extraction_id", sa.UUID(), primary_key=True),
        sa.Column("resume_id", sa.UUID(), sa.ForeignKey("resume_uploads.resume_id", ondelete="CASCADE"), nullable=False),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("extraction_status", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "resume_parsing_results",
        sa.Column("parsing_id", sa.UUID(), primary_key=True),
        sa.Column("resume_id", sa.UUID(), sa.ForeignKey("resume_uploads.resume_id", ondelete="CASCADE"), nullable=False),
        sa.Column("parsed_experience", sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("parsed_skills", sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("parsing_status", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "linkedin_imports",
        sa.Column("import_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_id", sa.UUID(), sa.ForeignKey("storage_files.file_id")),
        sa.Column("import_type", sa.String(50)),
        sa.Column("import_status", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "linkedin_parsed_data",
        sa.Column("parsed_id", sa.UUID(), primary_key=True),
        sa.Column("import_id", sa.UUID(), sa.ForeignKey("linkedin_imports.import_id", ondelete="CASCADE"), nullable=False),
        sa.Column("parsed_experience", sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("parsed_education", sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("parsed_skills", sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "profile_merge_operations",
        sa.Column("merge_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(50)),
        sa.Column("source_id", sa.UUID()),
        sa.Column("merge_status", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "encryption_keys",
        sa.Column("key_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("encrypted_key", sa.Text(), nullable=False),
        sa.Column("key_version", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "encrypted_tokens",
        sa.Column("token_id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_type", sa.String(50)),
        sa.Column("encrypted_value", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Seed cloud_providers
    op.execute(
        sa.text(
            "INSERT INTO cloud_providers (name) VALUES ('google_drive'), ('dropbox'), ('onedrive')"
        )
    )


def downgrade() -> None:
    op.drop_table("encrypted_tokens")
    op.drop_table("encryption_keys")
    op.drop_table("profile_merge_operations")
    op.drop_table("linkedin_parsed_data")
    op.drop_table("linkedin_imports")
    op.drop_table("resume_parsing_results")
    op.drop_table("resume_text_extraction")
    op.drop_table("resume_uploads")
    op.drop_table("storage_files")
    op.drop_table("storage_folders")
    op.drop_table("user_cloud_accounts")
    op.drop_table("sessions")
    op.drop_table("email_otps")
    op.drop_table("auth_providers")
    op.drop_index("ix_cloud_providers_name", table_name="cloud_providers")
    op.drop_table("cloud_providers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
