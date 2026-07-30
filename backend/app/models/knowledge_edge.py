"""
KnowledgeEdge model — one row per relationship between two KnowledgeNode
entities (Milestone 2: completing the Knowledge Graph that Sprint 8 Part 5
deliberately deferred).

Important asymmetry vs. KnowledgeNode, inherited from the Gemini schema,
not introduced here: app.extraction.extraction_schema.GeminiRelationship
has no evidence_quote field — relationships were never given direct
textual evidence, only entities were. So an edge's trustworthiness rests
entirely on both endpoints being independently verified KnowledgeNode
rows (see ExtractionService), not on its own quote. There is nothing to
verify a relationship's text against, because the Gemini response never
carried one — this file can't invent evidence that doesn't exist upstream.

relationship_type is a plain VARCHAR, not a Postgres enum — GeminiRelationship.
relationship_type is unconstrained free text on the Gemini side (no Literal,
unlike node_type), so an enum column would reject valid Gemini output.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    __table_args__ = (
        # Prevents duplicate edges if the same relationship is mentioned
        # more than once within a batch (or across batches for the same
        # two entities) — not a scenario that should be common, but cheap
        # to guard against a re-run producing duplicate graph edges.
        UniqueConstraint(
            "source_node_id", "target_node_id", "relationship_type",
            name="uq_knowledge_edges_source_target_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Same denormalization reasoning as KnowledgeNode.user_id — avoids a
    # join through knowledge_nodes for ownership-scoped graph queries.
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    source_node_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False, index=True
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False, index=True
    )

    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
