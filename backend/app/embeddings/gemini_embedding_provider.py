"""
Gemini implementation of EmbeddingProvider, using text-embedding-004.

The only file that imports google.genai for embeddings — mirrors
app/extraction/gemini_client.py's role for extraction (one file per API
surface owns the SDK dependency; everything else depends on the
abstraction). Reuses the same retry/backoff discipline established
there for transient failures (429/500/503).
"""

import logging
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import settings
from app.embeddings.embedding_provider import EmbeddingProvider

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "models/gemini-embedding-001"
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2, 4, 8)
_RETRYABLE_STATUS_CODES = {429, 500, 503}

# RETRIEVAL_DOCUMENT is the task type Gemini recommends for text that
# will later be searched against — used for everything EmbeddingService
# indexes. RETRIEVAL_QUERY is the counterpart for the search query
# itself (Sprint 8 Part 1) — Gemini's embedding model is asymmetric:
# embedding a query and a document differently (even for near-identical
# text) measurably improves retrieval quality versus using the same
# task type for both. text-embedding-004 supports this parameter
# (unlike some newer Gemini embedding models, where it's deprecated in
# favor of prompt-embedded task instructions).
_TASK_TYPE_DOCUMENT = "RETRIEVAL_DOCUMENT"
_TASK_TYPE_QUERY = "RETRIEVAL_QUERY"


class EmbeddingError(Exception):
    """Raised when Gemini embedding fails after all retry attempts."""


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        if not settings.gemini_api_key:
            raise EmbeddingError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = model

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._embed_with_task_type(texts, _TASK_TYPE_DOCUMENT)

    def embed_query(self, text: str) -> list[float]:
        return self._embed_with_task_type([text], _TASK_TYPE_QUERY)[0]

    def _embed_with_task_type(self, texts: list[str], task_type: str) -> list[list[float]]:
        if not texts:
            return []

        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = self._client.models.embed_content(
                    model=self._model,
                    contents=texts,
                    config=types.EmbedContentConfig(task_type=task_type),
                )
                return [embedding.values for embedding in response.embeddings]

            except genai_errors.APIError as exc:
                last_error = exc
                status_code = getattr(exc, "code", None)
                if status_code in _RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                    logger.warning(
                        "Gemini embed_content failed (status=%s, task_type=%s), retrying (%d/%d)",
                        status_code, task_type, attempt + 1, MAX_ATTEMPTS,
                    )
                    time.sleep(BACKOFF_SECONDS[attempt - 1])
                    continue
                break

        raise EmbeddingError(
            f"Gemini embedding failed after {MAX_ATTEMPTS} attempts: {last_error}"
        ) from last_error
