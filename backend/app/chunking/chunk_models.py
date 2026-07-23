"""
Internal chunk data structure — the output of ChunkGenerator, before it
becomes a DocumentChunk row. Kept separate from both the SQLAlchemy
model and the Pydantic schema so ChunkGenerator has no dependency on the
database or the API layer at all.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkData:
    chunk_index: int
    content: str
    start_offset: int
    end_offset: int
    character_count: int
    estimated_token_count: int
