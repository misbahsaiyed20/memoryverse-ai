"""
Abstract embedding provider interface.

Defines the contract every embedding backend must implement. Same
abstraction pattern as VectorStore/StorageService: EmbeddingService
depends on this interface, never a specific embedding API — swapping
Gemini for something else later means adding another EmbeddingProvider
subclass, not touching EmbeddingService or anything that calls it.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Return the embedding vector for a single piece of text."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a batch of texts, in the same
        order as the input list."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed text intended to be used as a search query.

        Distinct from embed_text()/embed_batch(), which embed text being
        indexed for later retrieval. Some providers (Gemini included) use
        an asymmetric embedding scheme where queries and indexed content
        are embedded differently for better retrieval quality — a
        provider that doesn't distinguish can simply delegate this to
        embed_text(). Added in Sprint 8 Part 1 for SearchService; every
        existing call to embed_text()/embed_batch() is unaffected.
        """
        raise NotImplementedError
