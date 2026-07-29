-- Sprint 8 Part 5 — manual schema update (Option A: no Alembic yet).
-- Run this once against your existing Postgres database before starting
-- the backend with the Sprint 8 Part 5 code. Safe to re-run.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'knowledge_node_entity_type') THEN
        CREATE TYPE knowledge_node_entity_type AS ENUM (
            'SKILL',
            'PROJECT',
            'CERTIFICATE',
            'ACHIEVEMENT',
            'ORGANIZATION',
            'EDUCATION',
            'INTERNSHIP',
            'TECHNOLOGY'
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS knowledge_nodes (
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

CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_user_id ON knowledge_nodes (user_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_document_chunk_id ON knowledge_nodes (document_chunk_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_entity_type ON knowledge_nodes (entity_type);