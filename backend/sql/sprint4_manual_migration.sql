-- Sprint 4 — manual schema update (Option A: no Alembic yet).
-- Run this once against your existing Postgres database before starting
-- the backend with the Sprint 4 code. Safe to re-run (IF NOT EXISTS guards).

ALTER TABLE documents ADD COLUMN IF NOT EXISTS extracted_text TEXT NULL;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ NULL;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_error TEXT NULL;
