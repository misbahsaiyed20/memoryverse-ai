"""
ChromaDB implementation of the VectorStore interface.

Uses a persistent local Chroma client (data survives process restarts —
consistent with the local-first storage choice already made for
document uploads; see LocalStorageService). The "career_brain"
collection is created automatically if it doesn't already exist;
creating it again on a later startup is a documented no-op via
get_or_create_collection(), not an error.

The Chroma client and its state live entirely on the instance
(self._client) — there is no module-level singleton here. A single
instance is constructed once at application startup (see main.py) and
handed out via app.state, not a global variable — see that file for why.
"""

import logging
from typing import Any

from chromadb import PersistentClient
from chromadb.errors import ChromaError

from app.embeddings.vector_store import VectorStore

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "career_brain"


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_path: str) -> None:
        """Initializes a persistent Chroma client rooted at persist_path.

        Does not create the collection here — call create_collection()
        explicitly (done once at app startup) so collection setup stays
        a visible, logged step rather than a side effect of construction.
        """
        self._persist_path = persist_path
        self._client = PersistentClient(path=persist_path)
        logger.info("Chroma persistent client initialized at path=%s", persist_path)

    def create_collection(self, name: str = DEFAULT_COLLECTION_NAME) -> None:
        try:
            self._client.get_or_create_collection(name=name)
            logger.info("Chroma collection ready: %s", name)
        except ChromaError:
            logger.exception("Failed to create/verify Chroma collection: %s", name)
            raise

    def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        try:
            collection = self._client.get_or_create_collection(name=collection_name)
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
            logger.info(
                "Upserted %d vector(s) into collection=%s", len(ids), collection_name
            )
        except ChromaError:
            logger.exception(
                "Failed to upsert %d vector(s) into collection=%s", len(ids), collection_name
            )
            raise

    def query(
        self,
        collection_name: str,
        query_embeddings: list[list[float]],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            collection = self._client.get_or_create_collection(name=collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
            )
            logger.info(
                "Queried collection=%s (n_results=%d, %d query vector(s))",
                collection_name, n_results, len(query_embeddings),
            )
            return results
        except ChromaError:
            logger.exception("Failed to query collection=%s", collection_name)
            raise

    def delete(self, collection_name: str, ids: list[str]) -> None:
        try:
            collection = self._client.get_or_create_collection(name=collection_name)
            collection.delete(ids=ids)
            logger.info(
                "Deleted %d vector(s) from collection=%s", len(ids), collection_name
            )
        except ChromaError:
            logger.exception(
                "Failed to delete %d vector(s) from collection=%s", len(ids), collection_name
            )
            raise

    def delete_document(self, collection_name: str, document_id: str) -> None:
        """Deletes every vector whose metadata carries this document_id.

        Assumes a convention future callers (EmbeddingService, Sprint 8+)
        must follow: every upsert() into this store should include
        "document_id" in that vector's metadata. Documenting the
        convention here since this method is what depends on it.
        """
        try:
            collection = self._client.get_or_create_collection(name=collection_name)
            collection.delete(where={"document_id": document_id})
            logger.info(
                "Deleted all vectors for document_id=%s from collection=%s",
                document_id, collection_name,
            )
        except ChromaError:
            logger.exception(
                "Failed to delete vectors for document_id=%s from collection=%s",
                document_id, collection_name,
            )
            raise

    def health_check(self) -> dict[str, Any]:
        """Never raises — reports failures in the returned dict instead,
        so a health endpoint (future sprint) can surface this cleanly."""
        database_reachable = False
        collection_exists = False

        try:
            self._client.heartbeat()
            database_reachable = True
            collection_names = {c.name for c in self._client.list_collections()}
            collection_exists = DEFAULT_COLLECTION_NAME in collection_names
        except Exception:
            logger.exception("Chroma health check failed")

        status = "healthy" if (database_reachable and collection_exists) else "unhealthy"

        return {
            "status": status,
            "collection_exists": collection_exists,
            "database_reachable": database_reachable,
        }
