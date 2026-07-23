"""
Chunking service.

All chunking orchestration lives here: ownership/precondition validation,
generation via ChunkGenerator, and storage. Routes only call into this.

Deliberately independent of DocumentProcessingService per the locked
architecture — chunking never runs automatically after processing, only
through its own endpoint, and this class has no dependency on that one.

Same two-entry-point split as Sprint 4's DocumentProcessingService, for
the same reason: validate_for_chunking() runs inside the request (using
the request-scoped session) so the response can be accurate immediately;
run()/generate_and_store() do the actual work in the background task,
with their own session since the request-scoped one is closed by then.
"""

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.chunking.chunk_generator import ChunkGenerator
from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def validate_for_chunking(self, document_id: uuid.UUID, user_id: int) -> Document:
        """Ownership + precondition checks, run synchronously in the request."""
        document = (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .one_or_none()
        )
        if document is None:
            # 404, not 403 — same rule as every other document endpoint.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        if document.status != DocumentStatus.PROCESSED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Document must be PROCESSED before it can be chunked "
                    f"(current status: {document.status.value})."
                ),
            )

        if not document.extracted_text:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document has no extracted text to chunk.",
            )

        if self._has_existing_chunks(document_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document has already been chunked.",
            )

        return document

    @classmethod
    def run(cls, document_id: uuid.UUID) -> None:
        """Background execution entry point — owns its own DB session,
        same pattern as DocumentProcessingService.run(). Takes nothing
        but a document ID, so swapping the dispatch mechanism later
        (see task_runner.py) requires no change here."""
        db = SessionLocal()
        try:
            service = cls(db)
            service.generate_and_store(document_id)
        finally:
            db.close()

    def generate_and_store(self, document_id: uuid.UUID) -> int:
        document = self.db.query(Document).filter(Document.id == document_id).one_or_none()
        if document is None:
            logger.error("Chunking skipped: document_id=%s no longer exists", document_id)
            return 0

        logger.info("Chunking started for document_id=%s", document_id)

        try:
            # Defensive re-check — request-time validation already
            # confirmed this, but the background task runs later and
            # shouldn't trust state that could have changed since.
            if not document.extracted_text:
                raise ValueError("Document has no extracted text to chunk.")

            if self._has_existing_chunks(document_id):
                logger.info(
                    "Chunking skipped for document_id=%s: chunks already exist", document_id
                )
                return self._has_existing_chunks(document_id, return_count=True)

            chunk_data_list = ChunkGenerator.generate(document.extracted_text)

            chunk_rows = [
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    character_count=chunk.character_count,
                    estimated_token_count=chunk.estimated_token_count,
                    start_offset=chunk.start_offset,
                    end_offset=chunk.end_offset,
                )
                for chunk in chunk_data_list
            ]
            self.db.add_all(chunk_rows)
            self.db.commit()

            # Log the count, never the content.
            logger.info(
                "Chunking completed for document_id=%s, chunk_count=%d",
                document_id,
                len(chunk_rows),
            )
            return len(chunk_rows)

        except Exception as exc:
            self.db.rollback()
            logger.error("Chunking failed for document_id=%s: %s", document_id, exc, exc_info=True)
            raise

    def _has_existing_chunks(self, document_id: uuid.UUID, return_count: bool = False):
        count = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .count()
        )
        return count if return_count else count > 0
