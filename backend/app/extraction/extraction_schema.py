"""
Schemas describing exactly what we ask Gemini to return, and what we
validate its response against on our side afterward.

Passed directly to Gemini as response_schema (the SDK supports Pydantic
models there) AND used to re-validate the parsed JSON ourselves — we
never trust the structured-output guarantee alone. Same "never
hallucinate, verify before storing" discipline as the rest of this
project.
"""

from typing import Literal

from pydantic import BaseModel, Field

NodeTypeLiteral = Literal[
    "SKILL",
    "PROJECT",
    "CERTIFICATE",
    "ACHIEVEMENT",
    "ORGANIZATION",
    "EDUCATION",
    "INTERNSHIP",
    "TECHNOLOGY",
]


class GeminiEntity(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    node_type: NodeTypeLiteral
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    # Exact verbatim substring from the source text supporting this
    # entity — required so we can resolve source_chunk_id afterward.
    evidence_quote: str = Field(..., min_length=1)
    class GeminiAttribute(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)


class GeminiEntity(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    node_type: NodeTypeLiteral
    description: str | None = None
    confidence: float |None = Field(default=None, ge=0.0, le=1.0)
    evidence_quote: str = Field(..., min_length=1)

    attributes: list[GeminiAttribute] = Field(default_factory=list)


class GeminiRelationship(BaseModel):
    # Referenced by name (matched against this same batch's entities),
    # not by ID — Gemini has no knowledge of our database IDs.
    source_entity_name: str = Field(..., min_length=1)
    target_entity_name: str = Field(..., min_length=1)
    relationship_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class GeminiExtractionResult(BaseModel):
    entities: list[GeminiEntity] = Field(default_factory=list)
    relationships: list[GeminiRelationship] = Field(default_factory=list)
