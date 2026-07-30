-- Sprint 8 Part 7 — schema repair.
-- Fixes environments where knowledge_nodes/knowledge_edges were created in
-- a stale shape (e.g. by create_all() running on an early backend startup
-- before sprint8_part5/6_manual_migration.sql were ever run) — the
-- reported symptom is "column knowledge_nodes.document_chunk_id does not
-- exist" despite the model/migration source files defining it correctly.
--
-- Safe to run: only drops these two tables if BOTH are confirmed empty.
-- If either has rows, it aborts and does nothing — re-run
-- sprint8_part5/6_manual_migration.sql by hand in that case instead.

DO $$
DECLARE
    node_count INTEGER;
    edge_count INTEGER;
BEGIN
    SELECT count(*) INTO node_count FROM knowledge_nodes;
    SELECT count(*) INTO edge_count FROM knowledge_edges;

    IF node_count > 0 OR edge_count > 0 THEN
        RAISE EXCEPTION
            'knowledge_nodes has % row(s), knowledge_edges has % row(s) — refusing to drop non-empty tables. Fix the schema manually instead.',
            node_count, edge_count;
    END IF;
END $$;

DROP TABLE IF EXISTS knowledge_edges;
DROP TABLE IF EXISTS knowledge_nodes;
DROP TYPE IF EXISTS knowledge_node_entity_type;

CREATE TYPE knowledge_node_entity_type AS ENUM (
    'SKILL', 'PROJECT', 'CERTIFICATE', 'ACHIEVEMENT',
    'ORGANIZATION', 'EDUCATION', 'INTERNSHIP', 'TECHNOLOGY'
);

CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    document_chunk_id UUID NOT NULL REFERENCES document_chunks(id),
    entity_type knowledge_node_entity_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    confidence FLOAT NULL,
    evidence_quote TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_knowledge_nodes_user_id ON knowledge_nodes (user_id);
CREATE INDEX ix_knowledge_nodes_document_chunk_id ON knowledge_nodes (document_chunk_id);
CREATE INDEX ix_knowledge_nodes_entity_type ON knowledge_nodes (entity_type);

CREATE TABLE knowledge_edges (
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

CREATE INDEX ix_knowledge_edges_user_id ON knowledge_edges (user_id);
CREATE INDEX ix_knowledge_edges_source_node_id ON knowledge_edges (source_node_id);
CREATE INDEX ix_knowledge_edges_target_node_id ON knowledge_edges (target_node_id);
