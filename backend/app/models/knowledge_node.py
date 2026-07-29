"""
KnowledgeNode model — one row per structured entity extracted from a
document chunk (Sprint 8 Part 5: Career Brain foundation).

Deliberately entities-only, no relationships/edges yet — that's a
later sprint once nodes exist to point at.

entity_type intentionally mirrors app.extraction.extraction_schema.
NODE_TYPES exactly (SKILL, PROJECT, CERTIFICATE, ACHIEVEMENT,
ORGANIZATION, EDUCATION, INTERNSHIP, TECHNOLOGY) rather than a
different/narrower list — that file is what Gemini is actually
prompted with and validated against (GeminiEntity.node_type), so this
enum has to be a superset-or-equal of it or valid extracted entities
would fail to persist. If NODE_TYPES ever changes, update both in the
same change plus a follow-up migration to alter the Postgres enum type.

Every row must carry evidence back to its source chunk — document_chunk_id
is non-nullable, same discipline as evidence_quote itself.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntityType(str, enum.Enum):
    SKILL = "SKILL"
    PROJECT = "PROJECT"
    CERTIFICATE = "CERTIFICATE"
    ACHIEVEMENT = "ACHIEVEMENT"
    ORGANIZATION = "ORGANIZATION"
    EDUCATION = "EDUCATION"
    INTERNSHIP = "INTERNSHIP"
    TECHNOLOGY = "TECHNOLOGY"


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Denormalized from documents.user_id via the owning document/chunk —
    # kept directly on the node (rather than joined through document_chunk
    # -> document every time) so ownership-scoped queries (e.g. "all of
    # this user's skills") don't need a join, matching the same reasoning
    # Document.user_id itself already uses.
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    document_chunk_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("document_chunks.id"), nullable=False, index=True
    )

    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="knowledge_node_entity_type"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Required, never nullable — this is the evidence linkage the whole
    # model exists to guarantee. Must appear verbatim in document_chunk_id's
    # content; ExtractionService discards any entity where that isn't true
    # before it ever reaches this table.
    evidence_quote: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )