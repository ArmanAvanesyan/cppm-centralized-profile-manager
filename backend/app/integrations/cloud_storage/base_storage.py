"""Base interface for cloud storage providers (OAuth + file operations)."""
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class BaseStorageClient(ABC):
    """Abstract base for Google Drive, Dropbox, OneDrive clients."""

    @abstractmethod
    def get_auth_url(self, db: Session, user_id: Any) -> str:
        """Return OAuth2 authorization URL. state should carry user_id for callback."""
        ...

    @abstractmethod
    def handle_callback(
        self,
        db: Session,
        code: str,
        state: str | None,
        user_id: Any | None,
    ) -> bool:
        """Exchange code for tokens, create/update account, create CPPM folder. Return True on success."""
        ...
