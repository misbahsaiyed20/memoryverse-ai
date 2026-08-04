"""
Extraction service — Sprint 8 Part 5 (nodes) + Part 6 (edges): Career
Brain foundation and graph completion.

Turns a document's already-generated chunks into persisted KnowledgeNode
and KnowledgeEdge rows, using the Gemini extraction machinery that
already existed (app.extraction.gemini_client.extract_from_text,
prompt_builder, extraction_schema) but had no service or route calling
it before Part 5.

Same validate_*()/run() two-entry-point naming as ChunkingService and
DocumentProcessingService, but run() is NOT dispatched through
BackgroundTasks/task_runner.py the way theirs are. Those services return
"started" immediately because nothing in their response depends on the
work finishing. This one has to report real nodes_created/edges_created
counts, which only exist once extraction is done — so run() executes
synchronously, inline in the request, sharing the same request-scoped
session as validate_for_extraction(). If a future sprint needs this
backgrounded (e.g. large documents making requests time out), that's a
route/task_runner change, not a change to this class's logic.

Never touches ChromaDB, embeddings, or SearchService — this class's
entire job is Postgres in (chunks), Gemini in the middle, Postgres out
(knowledge nodes + edges).

Edge verification is inherently weaker than node verification, and that
gap isn't something this file can close: GeminiRelationship has no
evidence_quote field (see extraction_schema.py), so there's no source
text to check a relationship against. What IS verified: both endpoints
must be entities that this same batch call actually extracted and that
independently passed evidence-quote verification as KnowledgeNode rows
— a relationship pointing at a name Gemini didn't actually return, or
at an entity that got discarded for failing its own verification, is
dropped.

Known limitation, inherent to the per-batch design (not introduced
here): a relationship can only be detected between two entities Gemini
saw in the *same* 5-chunk batch call. A skill mentioned in batch 1 and
a project mentioned in batch 4 will never get an edge between them,
even if the source document clearly relates them — Gemini has no memory
across batches. Closing that gap would mean resolving entity names
against the whole document (or the whole user's graph) rather than just
the current batch, which is a bigger design change than "finish the
graph" — flagging it rather than quietly leaving it undiscoverable.
"""

import logging
import uuid
from typing import NamedTuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.extraction.gemini_client import ExtractionError, extract_from_text
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_edge import KnowledgeEdge
from app.models.knowledge_node import EntityType, KnowledgeNode

logger = logging.getLogger(__name__)

# Matches the batching approach already documented in README.md's Sprint 6
# section ("documents chunk into groups of 5 for Gemini calls") — not
# reimplementing a different scheme, just finally giving it a home.
BATCH_SIZE = 5


class ExtractionSummary(NamedTuple):
    nodes_created: int
    edges_created: int


class _BatchResult(NamedTuple):
    nodes_created: int
    nodes_discarded: int
    edges_created: int
    edges_discarded: int


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

    def run(self, document: Document) -> ExtractionSummary:
        """Batches this document's chunks, calls Gemini extraction per
        batch, verifies each entity's evidence_quote against the actual
        chunk text, persists verified entities as KnowledgeNode rows,
        then persists relationships between them (within the same
        batch) as KnowledgeEdge rows.

        Never raises for a single batch's Gemini failure — logs it and
        continues with the next batch, same "one failure doesn't
        sacrifice the rest" discipline as
        EmbeddingService._embed_and_store_batch().
        """
        chunks = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        if not chunks:
            logger.warning("Extraction skipped: document_id=%s has no chunks", document.id)
            return ExtractionSummary(nodes_created=0, edges_created=0)

        logger.info(
            "Extraction started for document_id=%s, chunk_count=%d, batch_size=%d",
            document.id, len(chunks), BATCH_SIZE,
        )

        nodes_created = 0
        nodes_discarded = 0
        edges_created = 0
        edges_discarded = 0
        batches_failed = 0

        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[batch_start : batch_start + BATCH_SIZE]
            result = self._extract_and_store_batch(document, batch)
            if result is None:
                # The Gemini call itself failed for this batch — distinct
                # from a batch that succeeded but had nothing extractable
                # (that's a legitimate 0/0/0/0 result, not a failure).
                batches_failed += 1
                continue
            nodes_created += result.nodes_created
            nodes_discarded += result.nodes_discarded
            edges_created += result.edges_created
            edges_discarded += result.edges_discarded

        logger.info(
            "Extraction completed for document_id=%s: nodes_created=%d, "
            "nodes_discarded=%d, edges_created=%d, edges_discarded=%d, "
            "batches_failed=%d",
            document.id, nodes_created, nodes_discarded,
            edges_created, edges_discarded, batches_failed,
        )
        return ExtractionSummary(nodes_created=nodes_created, edges_created=edges_created)

    def _extract_and_store_batch(
        self, document: Document, batch: list[DocumentChunk]
    ) -> _BatchResult | None:
        batch_text = "\n\n".join(chunk.content for chunk in batch)

        try:
            result = extract_from_text(batch_text)
        except ExtractionError as exc:
            logger.warning(
                "Gemini extraction failed for document_id=%s (chunk_index %d-%d), "
                "skipping this batch: %s",
                document.id, batch[0].chunk_index, batch[-1].chunk_index, exc,
            )
            return None

        logger.info(
            "Batch extracted for document_id=%s: entities=%d, relationships=%d",
            document.id, len(result.entities), len(result.relationships),
        )

        node_rows: list[KnowledgeNode] = []
        nodes_by_name: dict[str, KnowledgeNode] = {}
        nodes_discarded = 0

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
                nodes_discarded += 1
                continue

            node = KnowledgeNode(
                user_id=document.user_id,
                document_chunk_id=matched_chunk.id,
                entity_type=EntityType(entity.node_type),
                name=entity.name,
                description=entity.description,
                confidence=entity.confidence,
                evidence_quote=entity.evidence_quote,
            )
            node_rows.append(node)
            # First-match wins if the same entity name appears twice in
            # one batch — a known, accepted limitation, not a crash risk.
            nodes_by_name.setdefault(entity.name, node)

        # Flush (not commit) node_rows now, before any edge references
        # node.id. KnowledgeNode.id's default (uuid.uuid4) is a
        # SQLAlchemy Python-side default — it's only resolved and
        # assigned onto the instance when the object is actually
        # flushed, not the moment KnowledgeNode(...) is constructed. Read
        # node.id before this point and every edge gets source_node_id=
        # NULL, which the DB then rejects — the whole batch's nodes
        # rolling back too, since the constraint violation happens
        # inside the same still-open transaction. Flushing here keeps
        # everything in one transaction (still rolled back together on
        # a later failure) while making the ids real before they're read.
        if node_rows:
            try:
                self.db.add_all(node_rows)
                self.db.flush()
            except Exception as exc:
                self.db.rollback()
                logger.error(
                    "Failed to flush %d knowledge node(s) for document_id=%s: %s",
                    len(node_rows), document.id, exc, exc_info=True,
                )
                return _BatchResult(0, nodes_discarded, 0, len(result.relationships))

        edge_rows: list[KnowledgeEdge] = []
        edges_discarded = 0

        for relationship in result.relationships:
            source_node = nodes_by_name.get(relationship.source_entity_name)
            target_node = nodes_by_name.get(relationship.target_entity_name)
            if source_node is None or target_node is None or source_node is target_node:
                # Relationship points at an entity name Gemini didn't
                # actually return this batch, or one that was discarded
                # above for failing its own evidence check, or names the
                # same entity on both ends. Discarded, not stored with a
                # dangling or self-referential edge.
                logger.warning(
                    "Discarding unverified relationship for document_id=%s: "
                    "%r -> %r (type=%s)",
                    document.id, relationship.source_entity_name,
                    relationship.target_entity_name, relationship.relationship_type,
                )
                edges_discarded += 1
                continue

            edge_rows.append(
                KnowledgeEdge(
                    user_id=document.user_id,
                    source_node_id=source_node.id,
                    target_node_id=target_node.id,
                    relationship_type=relationship.relationship_type,
                    description=relationship.description,
                    confidence=relationship.confidence,
                )
            )

        if node_rows or edge_rows:
            try:
                # node_rows were already added+flushed above (that's what
                # made their ids real for the edges above); only edge_rows
                # still need adding. Both remain in the same transaction,
                # so a failure here still rolls back the nodes too.
                self.db.add_all(edge_rows)
                self.db.commit()
            except Exception as exc:
                self.db.rollback()
                logger.error(
                    "Failed to store %d knowledge node(s) and %d edge(s) for "
                    "document_id=%s: %s",
                    len(node_rows), len(edge_rows), document.id, exc, exc_info=True,
                )
                return _BatchResult(0, nodes_discarded, 0, edges_discarded)

        return _BatchResult(len(node_rows), nodes_discarded, len(edge_rows), edges_discarded)

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
