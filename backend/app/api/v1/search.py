"""
Semantic search route.

Pure retrieval — no AI-generated answers, no summarization, no RAG, no
Gemini generate_content() call anywhere in this file. All orchestration
lives in SearchService; this route only wires dependencies, scopes
results to the authenticated user's own documents, and shapes the
response.

Security note: results are scoped to the current user's own document
IDs via a Chroma `where` filter, fetched fresh from Postgres on every
request. This is necessary because the vectors stored in ChromaDB
(Sprint 7 Part 2) carry no user_id in their metadata — without this
filter, any authenticated user could retrieve chunks from any other
user's documents. See SearchService.search()'s `where` parameter,
added specifically to support this.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_vector_store
from app.db.session import get_db
from app.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.embeddings.vector_store import VectorStore
from app.models.document import Document
from app.models.user import User
from app.services.search_service import DEFAULT_TOP_K, SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("query cannot be empty")
        return stripped


class SearchResultItem(BaseModel):
    document_id: str | None
    chunk_id: str | None
    chunk_text: str | None
    filename: str | None
    chunk_index: int | None
    metadata: dict
    distance: float | None


class SearchResponse(BaseModel):
    success: bool
    query: str
    results: list[SearchResultItem]


@router.post("", response_model=SearchResponse)
def search_documents(
    body: SearchRequest,
    current_user: User = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
    db: Session = Depends(get_db),
):
    logger.info(
        "Search started. user_id=%s, query=%r, top_k=%d",
        current_user.id, body.query, body.top_k,
    )

    try:
        owned_document_ids = [
            str(doc_id)
            for (doc_id,) in db.query(Document.id).filter(Document.user_id == current_user.id).all()
        ]

        if not owned_document_ids:
            # Nothing to search — not an error, just an empty scope.
            # Short-circuited here rather than passed through to Chroma:
            # an empty {"$in": []} filter is rejected by Chroma with a
            # ValueError, which SearchService would otherwise catch and
            # log as an exception for what is actually a completely
            # normal case (a user with no uploaded documents yet).
            logger.info(
                "Search skipped: user_id=%s owns no documents.", current_user.id
            )
            return SearchResponse(success=True, query=body.query, results=[])

        where = {"document_id": {"$in": owned_document_ids}}

        search_service = SearchService(
            embedding_provider=GeminiEmbeddingProvider(),
            vector_store=vector_store,
        )
        raw_results = search_service.search(query=body.query, top_k=body.top_k, where=where)

    except Exception:
        logger.exception(
            "Search failed. user_id=%s, query=%r", current_user.id, body.query
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again.",
        )

    logger.info("Matches found: %d. user_id=%s", len(raw_results), current_user.id)

    results = [
        SearchResultItem(
            document_id=r.get("document_id"),
            chunk_id=r.get("chunk_id"),
            chunk_text=r.get("text"),
            filename=r.get("filename"),
            chunk_index=r.get("chunk_index"),
            metadata=r.get("metadata") or {},
            distance=r.get("distance"),
        )
        for r in raw_results
    ]

    logger.info(
        "Search completed. user_id=%s, results_returned=%d", current_user.id, len(results)
    )

    return SearchResponse(success=True, query=body.query, results=results)
