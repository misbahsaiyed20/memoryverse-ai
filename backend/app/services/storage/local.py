"""
Local disk implementation of StorageService.

Files are stored flat under settings.upload_dir, named by a generated
UUID (never the user-supplied filename) — no path-traversal or filename
collision risk. The upload directory is created on first use if it
doesn't exist yet.

This is one StorageService implementation among possibly several — swap
in an S3StorageService later without touching DocumentService or any
route, since both only ever depend on the StorageService interface.
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.services.storage.base import StorageService

logger = logging.getLogger(__name__)


class LocalStorageService(StorageService):
    def __init__(self, upload_dir: str | None = None) -> None:
        self._upload_dir = Path(upload_dir or settings.upload_dir)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: BinaryIO, filename: str) -> str:
        """Write file content to disk under a generated UUID name.

        `filename` is only used to preserve the extension — the actual
        stored name is always UUID-generated. Returns that generated name,
        which becomes both `stored_filename` and `storage_path` in the DB.
        """
        extension = Path(filename).suffix.lower()
        generated_name = f"{uuid.uuid4()}{extension}"
        destination = self._upload_dir / generated_name

        with open(destination, "wb") as out_file:
            shutil.copyfileobj(file, out_file)

        return generated_name

    def get(self, reference: str) -> BinaryIO:
        path = self._resolve(reference)
        if not path.exists():
            raise FileNotFoundError(f"Stored file not found: {reference}")
        return open(path, "rb")

    def delete(self, reference: str) -> None:
        path = self._resolve(reference)
        try:
            path.unlink()
        except FileNotFoundError:
            # Idempotent by design — safe to call during orphan cleanup
            # even if the file was already removed.
            logger.warning("Tried to delete a file that no longer exists: %s", reference)

    def _resolve(self, reference: str) -> Path:
        # .name strips any directory components defensively — save() never
        # produces a nested reference, but get()/delete() shouldn't trust
        # an arbitrary caller-supplied reference not to try path traversal.
        return self._upload_dir / Path(reference).name
