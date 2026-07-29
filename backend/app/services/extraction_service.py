"""
Extraction service — Sprint 8 Part 5: Career Brain foundation.

Turns a document's already-generated chunks into persisted KnowledgeNode
rows, using the Gemini extraction machinery that already existed
(app.extraction.gemini_client.extract_from_text, prompt_builder,
extraction_schema) but had no service or route calling it before this
sprint.

Deliberately entities-only: GeminiExtractionResult also returns
relationships, but this service reads and discards them — relationship/
edge persistence is out of scope until nodes exist to connect (see
Sprint 8 Part 5 task notes).

Same validate_*()/run() two-entry-point naming as ChunkingService and
DocumentProcessingService, but run() is NOT dispatched through
BackgroundTasks/task_runner.py the way theirs are. Those services return
"started" immediately because nothing in their response depends on the
work finishing. This one has to report a real nodes_created count, which
only exists once extraction is done — so run() executes synchronously,
inline in the request, sharing the same request-scoped session as
validate_for_extraction(). If a future sprint needs this backgrounded
(e.g. large documents making requests time out), that's a route/
task_runner change, not a change to this class's logic.

Never touches ChromaDB, embeddings, or SearchService — this class's
entire job is Postgres in (chunks), Gemini in the middle, Postgres out
(knowledge nodes).
"""

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.extraction.gemini_client import ExtractionError, extract_from_text
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_node import EntityType, KnowledgeNode

logger = logging.getLogger(__name__)

# Matches the batching approach already documented in README.md's Sprint 6
# section ("documents chunk into groups of 5 for Gemini calls") — not
# reimplementing a different scheme, just finally giving it a home.
BATCH_SIZE = 5


class ExtractionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def validate_for_extraction(self, document_id: uuid.UUID, user_id: int) -> Document:
        """Ownership + precondition checks. Mirrors
        ChunkingService.validate_for_chunking()'s structure exactly."""
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
                    "Document must be PROCESSED before it can be extracted "
                    f"(current status: {document.status.value})."
                ),
            )

        chunk_count = (
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()
        )
        if chunk_count == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document has no chunks to extract from. Run /chunk first.",
            )

        if self._has_existing_nodes(document_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document has already been extracted.",
            )

        return document

    def run(self, document: Document) -> int:
        """Batches this document's chunks, calls Gemini extraction per
        batch, verifies each entity's evidence_quote against the actual
        chunk text, and persists verified entities as KnowledgeNode rows.

        Returns the number of nodes created. Never raises for a single
        batch's Gemini failure — logs it and continues with the next
        batch, same "one failure doesn't sacrifice the rest" discipline
        as EmbeddingService._embed_and_store_batch().
        """
        chunks = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        if not chunks:
            logger.warning("Extraction skipped: document_id=%s has no chunks", document.id)
            return 0

        logger.info(
            "Extraction started for document_id=%s, chunk_count=%d, batch_size=%d",
            document.id, len(chunks), BATCH_SIZE,
        )

        nodes_created = 0
        nodes_discarded = 0
        batches_failed = 0

        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[batch_start : batch_start + BATCH_SIZE]
            created, discarded = self._extract_and_store_batch(document, batch)
            nodes_created += created
            nodes_discarded += discarded
            if created == 0 and discarded == 0:
                batches_failed += 1

        logger.info(
            "Extraction completed for document_id=%s: nodes_created=%d, "
            "nodes_discarded=%d, batches_failed=%d",
            document.id, nodes_created, nodes_discarded, batches_failed,
        )
        return nodes_created

    def _extract_and_store_batch(
        self, document: Document, batch: list[DocumentChunk]
    ) -> tuple[int, int]:
        batch_text = "\n\n".join(chunk.content for chunk in batch)

        try:
            result = extract_from_text(batch_text)
        except ExtractionError as exc:
            logger.warning(
                "Gemini extraction failed for document_id=%s (chunk_index %d-%d), "
                "skipping this batch: %s",
                document.id, batch[0].chunk_index, batch[-1].chunk_index, exc,
            )
            return 0, 0

        # Relationships are intentionally read and discarded — entity/edge
        # persistence is a later sprint (see module docstring).
        logger.info(
            "Batch extracted for document_id=%s: entities=%d, relationships_ignored=%d",
            document.id, len(result.entities), len(result.relationships),
        )

        created = 0
        discarded = 0
        node_rows: list[KnowledgeNode] = []

        for entity in result.entities:
            matched_chunk = self._find_source_chunk(entity.evidence_quote, batch)
            if matched_chunk is None:
                # Never trust Gemini's output blindly — if the evidence
                # quote doesn't actually appear in any chunk in this
                # batch, the entity is discarded, not stored with a
                # best-guess or null chunk reference. Log the entity
                # name only, never chunk content.
                logger.warning(
                    "Discarding unverified entity for document_id=%s: name=%r, "
                    "type=%s (evidence_quote not found verbatim in source chunks)",
                    document.id, entity.name, entity.node_type,
                )
                discarded += 1
                continue

            node_rows.append(
                KnowledgeNode(
                    user_id=document.user_id,
                    document_chunk_id=matched_chunk.id,
                    entity_type=EntityType(entity.node_type),
                    name=entity.name,
                    description=entity.description,
                    confidence=entity.confidence,
                    evidence_quote=entity.evidence_quote,
                )
            )
            created += 1

        if node_rows:
            try:
                self.db.add_all(node_rows)
                self.db.commit()
            except Exception as exc:
                self.db.rollback()
                logger.error(
                    "Failed to store %d knowledge node(s) for document_id=%s: %s",
                    len(node_rows), document.id, exc, exc_info=True,
                )
                return 0, discarded

        return created, discarded

    @staticmethod
    def _find_source_chunk(
        evidence_quote: str, batch: list[DocumentChunk]
    ) -> DocumentChunk | None:
        """Returns the first chunk in `batch` whose content contains
        `evidence_quote` verbatim, or None if it appears in none of
        them. Exact substring match — the extraction prompt explicitly
        instructs Gemini to copy evidence_quote exactly from the source
        text, so this is a verification check, not a fuzzy search."""
        for chunk in batch:
            if evidence_quote and evidence_quote in chunk.content:
                return chunk
        return None

    def _has_existing_nodes(self, document_id: uuid.UUID) -> bool:
        return (
            self.db.query(KnowledgeNode)
            .join(DocumentChunk, KnowledgeNode.document_chunk_id == DocumentChunk.id)
            .filter(DocumentChunk.document_id == document_id)
            .first()
            is not None
        )