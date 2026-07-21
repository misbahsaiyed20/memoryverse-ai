"""
Document service layer.

All validation, storage orchestration, and DB writes for documents live
here — routes only call into this, they never touch storage or the
documents table directly.
"""

import io
import logging
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.services.storage.base import StorageService
from app.utils.file_validation import (
    get_extension,
    sanitize_filename,
    validate_extension,
    validate_mime_type,
    validate_size,
)

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_owned_or_404(self, document_id: uuid.UUID, user_id: int) -> Document:
        document = (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .one_or_none()
        )
        if document is None:
            # Deliberately 404, not 403 — a user who doesn't own this
            # document shouldn't learn that it exists at all.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        return document

    async def upload(self, user_id: int, upload_file: UploadFile, storage: StorageService) -> Document:
        original_filename = sanitize_filename(upload_file.filename or "unnamed")
        extension = get_extension(original_filename)
        validate_extension(extension)

        contents = await upload_file.read()
        validate_size(contents)

        mime_type = upload_file.content_type or "application/octet-stream"
        validate_mime_type(mime_type, extension)

        reference = storage.save(io.BytesIO(contents), original_filename)

        title = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename

        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=reference,
            title=title,
            file_extension=extension,
            mime_type=mime_type,
            file_size=len(contents),
            storage_path=reference,
            status=DocumentStatus.UPLOADED,
        )

        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            storage.delete(reference)  # avoid an orphaned file with no DB record
            logger.exception(
                "Failed to save document metadata; removed orphaned file %s", reference
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document. Please try again.",
            )

        return document

    def rename(self, document: Document, new_title: str) -> Document:
        document.title = new_title
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document, storage: StorageService) -> None:
        storage.delete(document.storage_path)
        self.db.delete(document)
        self.db.commit()
