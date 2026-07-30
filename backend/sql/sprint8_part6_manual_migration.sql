-- Sprint 8 Part 6 — manual schema update (Option A: no Alembic yet).
-- Continues sprint8_part5_manual_migration.sql — run that one first,
-- since this table's foreign keys reference knowledge_nodes.
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    source_node_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    target_node_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    relationship_type VARCHAR(100) NOT NULL,
    description TEXT NULL,
    confidence FLOAT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_knowledge_edges_source_target_type
        UNIQUE (source_node_id, target_node_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS ix_knowledge_edges_user_id ON knowledge_edges (user_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_edges_source_node_id ON knowledge_edges (source_node_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_edges_target_node_id ON knowledge_edges (target_node_id);
