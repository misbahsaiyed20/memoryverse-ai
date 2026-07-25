"""
Embedding service.

Loads a document's chunks from PostgreSQL, generates embeddings in
batches through an EmbeddingProvider, and stores them via the VectorStore
abstraction. Independent of every other pipeline stage (processing,
chunking, extraction) — Sprint 7 Part 2 is infrastructure + this service
only, nothing calls embed_document() yet (no routes, no background task
dispatch wired in this sprint).

Both EmbeddingProvider and VectorStore are injected via the constructor
— this class never imports google.genai or chromadb directly, matching
the same dependency-injection convention as DocumentService (storage)
and ExtractionService (Gemini via gemini_client).
"""

import logging
import uuid

from sqlalchemy.orm import Session

from app.embeddings.embedding_provider import EmbeddingProvider
from app.embeddings.vector_store import VectorStore
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 20

# Matches ChromaVectorStore.DEFAULT_COLLECTION_NAME (Sprint 7 Part 1).
# Not imported directly to avoid coupling EmbeddingService to the Chroma
# implementation specifically — it only depends on the VectorStore
# interface, per the collection name being a plain string parameter.
COLLECTION_NAME = "career_brain"


class EmbeddingService:
    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.db = db
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.batch_size = batch_size

    def embed_document(self, document_id: uuid.UUID) -> int:
        """Embeds every chunk of a document and stores the resulting
        vectors. Returns the number of chunks successfully embedded and
        stored. Never raises for an individual chunk failure — logs it
        and continues with the rest, per Sprint 7 Part 2 requirements.
        """
        document = self.db.query(Document).filter(Document.id == document_id).one_or_none()
        if document is None:
            logger.error("Embedding skipped: document_id=%s no longer exists", document_id)
            return 0

        chunks = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        if not chunks:
            logger.warning("Embedding skipped: document_id=%s has no chunks", document_id)
            return 0

        logger.info(
            "Embedding started for document_id=%s, chunk_count=%d, batch_size=%d",
            document_id, len(chunks), self.batch_size,
        )

        succeeded = 0
        for batch_start in range(0, len(chunks), self.batch_size):
            batch = chunks[batch_start : batch_start + self.batch_size]
            succeeded += self._embed_and_store_batch(document, batch)
            logger.info(
                "Embedding progress for document_id=%s: %d/%d chunks done",
                document_id, min(batch_start + len(batch), len(chunks)), len(chunks),
            )

        logger.info(
            "Embedding completed for document_id=%s: %d/%d chunks succeeded",
            document_id, succeeded, len(chunks),
        )
        return succeeded

    def _embed_and_store_batch(self, document: Document, batch: list[DocumentChunk]) -> int:
        texts = [chunk.content for chunk in batch]

        try:
            vectors = self.embedding_provider.embed_batch(texts)
        except Exception as exc:
            # The whole batch call failed — fall back to embedding one
            # chunk at a time so a single bad chunk doesn't sacrifice
            # every other chunk in this batch.
            logger.warning(
                "Batch embedding call failed for document_id=%s (chunk_index %d-%d), "
                "falling back to per-chunk embedding: %s",
                document.id, batch[0].chunk_index, batch[-1].chunk_index, exc,
            )
            return self._embed_and_store_individually(document, batch)

        ids = [f"chunk_{chunk.id}" for chunk in batch]
        metadatas = [self._build_metadata(document, chunk) for chunk in batch]

        try:
            self.vector_store.upsert(
                collection_name=COLLECTION_NAME,
                ids=ids,
                embeddings=vectors,
                metadatas=metadatas,
                documents=texts,
            )
            return len(batch)
        except Exception as exc:
            logger.error(
                "Failed to store batch of %d embedding(s) for document_id=%s: %s",
                len(batch), document.id, exc, exc_info=True,
            )
            # Vectors were computed but storage failed — retry storage
            # per-chunk rather than losing the whole batch's work.
            return self._embed_and_store_individually(document, batch)

    def _embed_and_store_individually(
        self, document: Document, chunks: list[DocumentChunk]
    ) -> int:
        """Fallback path — one chunk at a time, so a single failure only
        costs that one chunk instead of the whole batch."""
        succeeded = 0
        for chunk in chunks:
            try:
                vector = self.embedding_provider.embed_text(chunk.content)
                self.vector_store.upsert(
                    collection_name=COLLECTION_NAME,
                    ids=[f"chunk_{chunk.id}"],
                    embeddings=[vector],
                    metadatas=[self._build_metadata(document, chunk)],
                    documents=[chunk.content],
                )
                succeeded += 1
            except Exception as exc:
                logger.error(
                    "Failed to embed/store chunk_id=%s (document_id=%s): %s",
                    chunk.id, document.id, exc, exc_info=True,
                )
                # Continue with the remaining chunks — one failure
                # shouldn't abort the rest of the document.
                continue
        return succeeded

    @staticmethod
    def _build_metadata(document: Document, chunk: DocumentChunk) -> dict:
        return {
            "document_id": str(document.id),
            "chunk_id": str(chunk.id),
            "filename": document.original_filename,
            "mime_type": document.mime_type,
            # Not tracked anywhere in the pipeline today — chunking
            # (Sprint 5) operates on the whole extracted_text as one
            # string, with no page-boundary information surviving from
            # PDF extraction (Sprint 4 concatenates all pages together).
            # Included as required, but ChromaVectorStore's underlying
            # client drops None-valued metadata keys entirely rather
            # than storing them (verified directly) — so this key will
            # not actually appear on stored records until a future
            # sprint adds real page tracking through the pipeline.
            "page": None,
            "chunk_index": chunk.chunk_index,
        }
