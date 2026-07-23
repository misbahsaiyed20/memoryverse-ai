"""
DocumentChunk schema — metadata only.

`content` is deliberately excluded: "never expose chunk content through
the API" is a stated security requirement for this sprint. No route
currently returns this schema (Sprint 5 has no chunk-listing endpoint),
but it's registered now — same convention as every other model — so a
future read-only listing endpoint has a ready-made, already-safe shape
to use.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document_chunk import DocumentChunk


class DocumentChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    character_count: int
    estimated_token_count: int
    start_offset: int
    end_offset: int
    created_at: datetime

    @classmethod
    def from_chunk(cls, chunk: DocumentChunk) -> "DocumentChunkOut":
        return cls(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            character_count=chunk.character_count,
            estimated_token_count=chunk.estimated_token_count,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
            created_at=chunk.created_at,
        )
