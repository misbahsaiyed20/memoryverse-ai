"""
Verse AI service.

Orchestrates single-turn Retrieval-Augmented Generation: retrieve
relevant chunks for a question (scoped to one user's own documents),
then ask Gemini to answer using only that evidence. No chat memory, no
streaming, no hallucination — if the evidence doesn't support an
answer, Gemini is instructed to say so explicitly.

Reuses SearchService (constructor-injected, same DI pattern as every
other service in this project) and gemini_client.generate_text() (the
existing Gemini client singleton and retry discipline — see that
file's docstring for why a new function was added there rather than
reusing extract_from_text(), which is hardwired to a different,
incompatible response schema).
"""

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.extraction.gemini_client import GeminiGenerationError, generate_text
from app.models.document import Document
from app.services.search_service import DEFAULT_TOP_K, SearchService

logger = logging.getLogger(__name__)

NO_EVIDENCE_ANSWER = "I couldn't find relevant information in your uploaded documents."
GENERATION_FAILURE_ANSWER = "Something went wrong while generating your answer. Please try again."

_SYSTEM_INSTRUCTIONS = """You are MemoryVerse AI.
Answer ONLY using the supplied evidence.
Never use outside knowledge.
If the evidence is insufficient, explicitly say you don't know.
Do not fabricate experience, skills, education or certifications.

Additional rules:
- Answer only using the supplied document chunks below.
- Never invent information that isn't stated in the evidence.
- If information needed to answer is missing from the evidence, say so explicitly.
- Be concise and professional.
- If the evidence only partially supports an answer, mention that uncertainty."""


class VerseAIService:
    def __init__(self, db: Session, search_service: SearchService) -> None:
        self.db = db
        self.search_service = search_service

    def ask(
        self,
        question: str,
        user_id: uuid.UUID,
        top_k: int = DEFAULT_TOP_K,
    ) -> dict[str, Any]:
        """Answer `question` using only this user's own indexed document
        chunks as evidence. Never raises — every failure path (blank
        question, no matching evidence, search failure, Gemini failure)
        returns a structured, safe response instead.
        """
        question = (question or "").strip() if isinstance(question, str) else ""
        if not question:
            logger.warning("Verse AI: blank question received for user_id=%s.", user_id)
            return {"success": False, "answer": "", "sources": []}

        logger.info(
            "Verse AI: question received. user_id=%s, question_length=%d, top_k=%d",
            user_id, len(question), top_k,
        )

        try:
            owned_document_ids = [
                str(doc_id)
                for (doc_id,) in self.db.query(Document.id).filter(Document.user_id == user_id).all()
            ]
        except Exception:
            logger.exception("Verse AI: failed to look up user's documents. user_id=%s", user_id)
            return {"success": False, "answer": GENERATION_FAILURE_ANSWER, "sources": []}

        if not owned_document_ids:
            logger.info("Verse AI: user_id=%s owns no documents — no evidence possible.", user_id)
            return {"success": True, "answer": NO_EVIDENCE_ANSWER, "sources": []}

        try:
            chunks = self.search_service.search(
                query=question,
                top_k=top_k,
                where={"document_id": {"$in": owned_document_ids}},
            )
        except Exception:
            logger.exception("Verse AI: search failed. user_id=%s", user_id)
            return {"success": False, "answer": GENERATION_FAILURE_ANSWER, "sources": []}

        logger.info("Verse AI: chunks retrieved. user_id=%s, chunk_count=%d", user_id, len(chunks))

        if not chunks:
            logger.info("Verse AI: no relevant chunks found. user_id=%s", user_id)
            return {"success": True, "answer": NO_EVIDENCE_ANSWER, "sources": []}

        prompt = self._build_prompt(question, chunks)

        logger.info("Verse AI: Gemini request started. user_id=%s", user_id)
        try:
            answer = generate_text(prompt)
        except GeminiGenerationError:
            logger.exception("Verse AI: Gemini generation failed. user_id=%s", user_id)
            return {"success": False, "answer": GENERATION_FAILURE_ANSWER, "sources": []}
        except Exception:
            logger.exception("Verse AI: unexpected error calling Gemini. user_id=%s", user_id)
            return {"success": False, "answer": GENERATION_FAILURE_ANSWER, "sources": []}

        logger.info("Verse AI: Gemini response received. user_id=%s", user_id)

        if not answer:
            logger.warning(
                "Verse AI: Gemini returned an empty response. user_id=%s",
                user_id,
                )
            return {
                "success": False,
                "answer": GENERATION_FAILURE_ANSWER,
                "sources": [],
            }

        sources = self._build_sources(chunks)

        logger.info(
             "Verse AI: answer returned. user_id=%s, source_count=%d",
             user_id,
             len(sources),
            )

        return {
            "success": True,
            "answer": answer.strip(),
            "sources": sources,
        }


    @staticmethod
    def _build_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
        evidence_blocks = "\n\n".join(
            f"Evidence {i}:\n{chunk.get('text', '')}"
            for i, chunk in enumerate(chunks, start=1)
        )
        return (
            f"{_SYSTEM_INSTRUCTIONS}\n\n"
            f"---\nEVIDENCE:\n{evidence_blocks}\n---\n\n"
            f"QUESTION: {question}"
        )

    @staticmethod
    def _build_sources(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Deliberately excludes chunk text — sources cite provenance,
        # never raw content, matching the "never expose chunk content"
        # principle already established for chunking (Sprint 5) and
        # extraction (Sprint 6).
        return [
            {
                "document_id": chunk.get("document_id"),
                "filename": chunk.get("filename"),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index"),
                "distance": chunk.get("distance"),
            }
            for chunk in chunks
        ]
