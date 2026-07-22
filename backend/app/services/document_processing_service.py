"""
Document processing service.

Owns the entire processing lifecycle: validating the document and its
status, selecting a processor, extracting and normalizing text, storing
the result, and handling failures — all in one place, per the locked
architecture.

Two entry points, deliberately separate because they run in different
contexts:

- mark_processing(): runs inside the request/response cycle, using the
  request-scoped DB session. Does validation + the UPLOADED/FAILED ->
  PROCESSING transition, so the API response can truthfully report
  status="PROCESSING" before returning.

- run() / extract_and_store(): the actual extraction work, executed
  by the background task after the response has already been sent.
  Cannot reuse the request-scoped session (it's closed by then), so
  run() opens its own via SessionLocal().

`run(document_id)` is the loose-coupling seam: it takes nothing but a
document ID and manages its own dependencies end to end. Swapping the
execution mechanism later (BackgroundTasks -> Celery, etc. — see
app/services/task_runner.py) means changing only how run() gets called,
never its body or anything in this class.
"""

import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.processors.factory import ProcessorFactory
from app.processors.normalizer import TextNormalizer
from app.services.storage.base import StorageService

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def mark_processing(self, document_id: uuid.UUID, user_id: int) -> Document:
        """Validate ownership + status, then transition to PROCESSING.

        Runs synchronously as part of the request so the API response
        can report the new status immediately — the actual extraction
        happens afterward, in the background.
        """
        document = (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .one_or_none()
        )
        if document is None:
            # 404, not 403 — don't reveal that the document exists at all
            # to a user who doesn't own it (same rule as Sprint 3).
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        if document.status not in (DocumentStatus.UPLOADED, DocumentStatus.FAILED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document cannot be processed while status is {document.status.value}.",
            )

        document.status = DocumentStatus.PROCESSING
        document.processing_error = None
        self.db.commit()
        self.db.refresh(document)

        logger.info("Processing started for document_id=%s", document_id)
        return document

    @classmethod
    def run(cls, document_id: uuid.UUID) -> None:
        """Background execution entry point — owns its own DB session and
        storage instance since it runs outside any request context."""
        # Local import to avoid a circular import at module load time
        # (deps -> this service would otherwise import each other).
        from app.api.deps import get_storage_service

        db = SessionLocal()
        try:
            service = cls(db)
            service.extract_and_store(document_id, get_storage_service())
        finally:
            db.close()

    def extract_and_store(self, document_id: uuid.UUID, storage: StorageService) -> None:
        document = self._get_document(document_id)
        if document is None:
            logger.error("Processing skipped: document_id=%s no longer exists", document_id)
            return

        tmp_path: str | None = None
        try:
            processor = ProcessorFactory.get_processor(document.file_extension)
            logger.info(
                "Selected processor=%s for document_id=%s",
                type(processor).__name__,
                document_id,
            )

            file_obj = storage.get(document.storage_path)
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=f".{document.file_extension}", delete=False
                ) as tmp:
                    shutil.copyfileobj(file_obj, tmp)
                    tmp_path = tmp.name
            finally:
                file_obj.close()

            raw_text = processor.extract_text(tmp_path)
            logger.info("Extraction completed for document_id=%s", document_id)

            normalized_text = TextNormalizer.normalize(raw_text)

            document.extracted_text = normalized_text
            document.processed_at = datetime.now(timezone.utc)
            document.status = DocumentStatus.PROCESSED
            document.processing_error = None
            self.db.commit()

            logger.info("Processing completed for document_id=%s", document_id)

        except Exception as exc:
            # Never log extracted_text/raw_text here — only metadata.
            logger.error("Processing failed for document_id=%s: %s", document_id, exc, exc_info=True)
            self.db.rollback()
            self._mark_failed(document_id, str(exc))

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _get_document(self, document_id: uuid.UUID) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).one_or_none()

    def _mark_failed(self, document_id: uuid.UUID, error_message: str) -> None:
        # Re-fetch after rollback — the previous instance is expired.
        document = self._get_document(document_id)
        if document is None:
            return
        document.status = DocumentStatus.FAILED
        document.processing_error = error_message
        self.db.commit()
