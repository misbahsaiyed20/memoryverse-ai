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

# Exported for gemini_client.py
NODE_TYPES = [
    "SKILL",
    "PROJECT",
    "CERTIFICATE",
    "ACHIEVEMENT",
    "ORGANIZATION",
    "EDUCATION",
    "INTERNSHIP",
    "TECHNOLOGY",
]

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


class GeminiAttribute(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)


class GeminiEntity(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    node_type: NodeTypeLiteral
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_quote: str = Field(..., min_length=1)
    attributes: list[GeminiAttribute] = Field(default_factory=list)


class GeminiRelationship(BaseModel):
    source_entity_name: str = Field(..., min_length=1)
    target_entity_name: str = Field(..., min_length=1)
    relationship_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class GeminiExtractionResult(BaseModel):
    entities: list[GeminiEntity] = Field(default_factory=list)
    relationships: list[GeminiRelationship] = Field(default_factory=list)