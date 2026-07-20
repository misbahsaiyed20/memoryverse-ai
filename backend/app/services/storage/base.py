"""
Storage service interface.

Placeholder only — no concrete implementation yet. This exists so upload
handling (added in a later sprint) is written against an interface, not a
specific storage backend. When local disk storage is implemented, it becomes
one `StorageService` subclass; swapping to S3/GCS later means adding another
subclass, not touching any code that calls this interface.

Do not implement upload logic here yet — Sprint 1 scope is the interface only.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    """Abstract interface all storage backends must implement."""

    @abstractmethod
    def save(self, file: BinaryIO, filename: str) -> str:
        """Persist a file and return a reference (path, key, or URL) to it."""
        raise NotImplementedError

    @abstractmethod
    def get(self, reference: str) -> BinaryIO:
        """Retrieve a previously stored file by its reference."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, reference: str) -> None:
        """Delete a previously stored file by its reference."""
        raise NotImplementedError
