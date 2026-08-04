"""Career Brain query service — reads KnowledgeNode/KnowledgeEdge only.
Never touches Chroma/Gemini; this is pure Postgres querying over what
ExtractionService already persisted."""

import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_edge import KnowledgeEdge
from app.models.knowledge_node import EntityType, KnowledgeNode


class CareerBrainService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_entity_counts(self, user_id: int) -> dict[str, int]:
        """Canonical counts-by-type. DashboardService composes this
        rather than re-querying knowledge_nodes itself."""
        rows = (
            self.db.query(KnowledgeNode.entity_type, func.count(KnowledgeNode.id))
            .filter(KnowledgeNode.user_id == user_id)
            .group_by(KnowledgeNode.entity_type)
            .all()
        )
        counts = {t.value: 0 for t in EntityType}
        for entity_type, count in rows:
            counts[entity_type.value] = count
        return counts

    def get_nodes(
        self, user_id: int, entity_type: EntityType | None = None, related_to: str | None = None
    ) -> list[dict]:
        """Evidence-backed node listing. related_to filters to nodes with
        an edge (either direction) to a node whose name matches
        case-insensitively — covers "projects that use Python" by
        passing entity_type=PROJECT&related_to=Python."""
        query = (
            self.db.query(KnowledgeNode, DocumentChunk, Document)
            .join(DocumentChunk, KnowledgeNode.document_chunk_id == DocumentChunk.id)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(KnowledgeNode.user_id == user_id)
        )
        if entity_type is not None:
            query = query.filter(KnowledgeNode.entity_type == entity_type)

        if related_to:
            related_node_ids = (
                self.db.query(KnowledgeNode.id)
                .filter(KnowledgeNode.user_id == user_id, KnowledgeNode.name.ilike(related_to))
                .subquery()
            )
            edge_partner_ids = (
                self.db.query(KnowledgeEdge.target_node_id)
                .filter(KnowledgeEdge.source_node_id.in_(related_node_ids))
                .union(
                    self.db.query(KnowledgeEdge.source_node_id).filter(
                        KnowledgeEdge.target_node_id.in_(related_node_ids)
                    )
                )
                .subquery()
            )
            query = query.filter(KnowledgeNode.id.in_(self.db.query(edge_partner_ids)))

        results = query.order_by(KnowledgeNode.created_at.desc()).all()
        return [self._serialize(node, chunk, doc) for node, chunk, doc in results]

    def get_timeline(self, user_id: int) -> list[dict]:
        """One entry per document, chronological by document creation,
        each carrying the entities extracted from it."""
        documents = (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.asc())
            .all()
        )
        timeline = []
        for document in documents:
            results = (
                self.db.query(KnowledgeNode, DocumentChunk)
                .join(DocumentChunk, KnowledgeNode.document_chunk_id == DocumentChunk.id)
                .filter(DocumentChunk.document_id == document.id)
                .order_by(KnowledgeNode.created_at.asc())
                .all()
            )
            if not results:
                continue
            timeline.append(
                {
                    "document_id": str(document.id),
                    "filename": document.title,
                    "created_at": document.created_at.isoformat(),
                    "nodes": [self._serialize(node, chunk, document) for node, chunk in results],
                }
            )
        return timeline

    def get_edges(self, user_id: int) -> list[dict]:
        edges = self.db.query(KnowledgeEdge).filter(KnowledgeEdge.user_id == user_id).all()
        return [
            {
                "id": str(edge.id),
                "source_node_id": str(edge.source_node_id),
                "target_node_id": str(edge.target_node_id),
                "relationship_type": edge.relationship_type,
                "description": edge.description,
                "confidence": edge.confidence,
            }
            for edge in edges
        ]

    @staticmethod
    def _serialize(node: KnowledgeNode, chunk: DocumentChunk, document: Document) -> dict:
        return {
            "id": str(node.id),
            "entity_type": node.entity_type.value,
            "name": node.name,
            "description": node.description,
            "confidence": node.confidence,
            "evidence_quote": node.evidence_quote,
            "document_id": str(document.id),
            "filename": document.title,
            "chunk_id": str(chunk.id),
        }
