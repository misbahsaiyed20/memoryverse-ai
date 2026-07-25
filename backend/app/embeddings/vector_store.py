"""
Abstract vector store interface.

Defines the contract every vector store backend must implement. No
implementation lives here — see chroma_vector_store.py for the first
concrete backend (Sprint 7). Mirrors the same abstraction pattern as
StorageService (Sprint 1/3): callers depend on this interface, never on
a specific vector database, so swapping Chroma for something else later
means adding another VectorStore subclass, not touching any calling code.

Sprint 7 scope: infrastructure only. Nothing in this project calls these
methods yet — EmbeddingService and SearchService don't exist yet, and
won't until a future sprint.
"""

from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    @abstractmethod
    def create_collection(self, name: str) -> None:
        """Create a collection if it doesn't already exist. No-op if it does."""
        raise NotImplementedError

    @abstractmethod
    def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        """Insert new vectors or overwrite existing ones (matched by id)."""
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        collection_name: str,
        query_embeddings: list[list[float]],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return the n_results nearest neighbors for each query embedding,
        optionally filtered by a metadata `where` clause."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, collection_name: str, ids: list[str]) -> None:
        """Delete specific vectors by id."""
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, collection_name: str, document_id: str) -> None:
        """Delete every vector associated with a given document_id.

        Distinct from delete() because callers won't always know
        individual vector ids up front (e.g. "this document was
        deleted, remove all its chunks' vectors") — this is the
        document-level cleanup path.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Return a status dict describing reachability and readiness —
        never raises; callers get a structured result either way."""
        raise NotImplementedError
