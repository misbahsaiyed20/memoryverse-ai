"""
Verse AI route.

Provides Retrieval-Augmented Generation (RAG) over the authenticated
user's uploaded documents.

Pipeline:

Question
    ↓
VerseAIService
    ↓
SearchService
    ↓
Gemini
    ↓
Answer
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_vector_store
from app.db.session import get_db
from app.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.embeddings.vector_store import VectorStore
from app.models.user import User
from app.schemas.verse import VerseRequest, VerseResponse
from app.services.search_service import SearchService
from app.services.verse_ai_service import VerseAIService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/verse",
    tags=["Verse AI"],
)


@router.post("/ask", response_model=VerseResponse)
def ask_question(
    body: VerseRequest,
    current_user: User = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
    db: Session = Depends(get_db),
):
    """
    Answer a question using Retrieval-Augmented Generation (RAG)
    over the authenticated user's uploaded documents.
    """

    logger.info(
        "VerseAI request started. user_id=%s",
        current_user.id,
    )

    try:
        search_service = SearchService(
            embedding_provider=GeminiEmbeddingProvider(),
            vector_store=vector_store,
        )

        verse_service = VerseAIService(
            db=db,
            search_service=search_service,
        )

        result = verse_service.ask(
            question=body.question,
            user_id=current_user.id,
            top_k=body.top_k,
        )

        logger.info(
            "VerseAI completed. success=%s",
            result["success"],
        )

        return VerseResponse(**result)

    except Exception:
        logger.exception(
            "VerseAI failed. user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verse AI request failed. Please try again.",
        )