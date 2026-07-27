"""
Search service.

Orchestrates semantic retrieval: embeds a query, searches the vector
store, and returns matching chunks with their metadata. No AI-generated
answers, no chat, no RAG — pure retrieval, per Sprint 8 Part 1 scope.

Both dependencies (EmbeddingProvider, VectorStore) are constructor-
injected, exactly like EmbeddingService — this class never imports
google.genai or chromadb directly.
"""

import logging
from typing import Any

from app.embeddings.embedding_provider import EmbeddingProvider
from app.embeddings.vector_store import VectorStore

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5

# Matches EmbeddingService.COLLECTION_NAME / ChromaVectorStore's
# "career_brain" default — not imported directly, to keep SearchService
# decoupled from any specific VectorStore implementation, same reasoning
# as EmbeddingService's own COLLECTION_NAME constant.
COLLECTION_NAME = "career_brain"


class SearchService:
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Embed `query` and return the top_k most similar stored chunks.

        `where` is an opaque Chroma-style metadata filter, forwarded
        as-is to VectorStore.query() — SearchService doesn't interpret
        it. Added so a caller (the /search route) can scope results to
        a specific set of documents (e.g. "only this user's own
        documents") without SearchService needing to know anything
        about users, ownership, or Postgres — that stays entirely the
        caller's responsibility, keeping this class's job exactly what
        it was in Sprint 8 Part 1: embed a query, search, return
        results. Omitting `where` preserves every existing behavior
        exactly (default None).

        Never raises: an empty/invalid query, an empty vector store, or
        an embedding/query failure all result in an empty list plus a
        logged reason — callers can treat "no results" and "search
        failed" the same way at this layer (Sprint 8 Part 1 is retrieval
        infrastructure only; deciding how to surface failures to a user
        is a future sprint's concern once routes exist).
        """
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            logger.warning("Search called with an empty or invalid query — returning no results.")
            return []

        if top_k <= 0:
            logger.warning(
                "Search called with non-positive top_k=%s — returning no results.", top_k
            )
            return []

        logger.info("Search started. query_length=%d, top_k=%d", len(query), top_k)

        try:
            query_embedding = self.embedding_provider.embed_query(query)
        except Exception:
            logger.exception("Search failed: could not generate query embedding.")
            return []

        try:
            raw_results = self.vector_store.query(
                collection_name=COLLECTION_NAME,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
            )
        except Exception:
            logger.exception("Search failed: vector store query error.")
            return []

        results = self._format_results(raw_results)
        logger.info("Search completed. results_returned=%d", len(results))
        return results

    @staticmethod
    def _format_results(raw_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Chroma's query() nests everything one level deep — one list
        per query embedding, since it supports batched queries. search()
        only ever sends a single query embedding, so this unwraps that
        one outer layer into a flat list of results.
        """
        ids = (raw_results.get("ids") or [[]])[0]
        if not ids:
            return []

        distances = (raw_results.get("distances") or [[]])[0]
        metadatas = (raw_results.get("metadatas") or [[]])[0]
        documents = (raw_results.get("documents") or [[]])[0]

        formatted: list[dict[str, Any]] = []
        for i, _vector_id in enumerate(ids):
            metadata = metadatas[i] if i < len(metadatas) else {}
            formatted.append(
                {
                    "chunk_id": metadata.get("chunk_id"),
                    "document_id": metadata.get("document_id"),
                    "filename": metadata.get("filename"),
                    "chunk_index": metadata.get("chunk_index"),
                    # Raw distance from the vector store's default
                    # metric — for ChromaVectorStore's "career_brain"
                    # collection, that's unconfigured squared L2 (no
                    # explicit metric was set when the collection was
                    # created in Sprint 7 Part 1). Lower = more similar.
                    # Not normalized into a bounded 0-1 "similarity"
                    # score: that requires a known, fixed metric (e.g.
                    # cosine), which would mean recreating the existing
                    # collection with that metric configured — a
                    # breaking change to already-stored embeddings, out
                    # of scope for this sprint. See design notes.
                    "distance": distances[i] if i < len(distances) else None,
                    "text": documents[i] if i < len(documents) else None,
                    "metadata": metadata,
                }
            )
        return formatted
