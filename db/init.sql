-- The app runs without pgvector by storing deterministic embeddings as text.
-- Swap this to `vector(1536)` after installing pgvector if you want ANN search.

CREATE TABLE IF NOT EXISTS companies (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    sector      TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id           BIGSERIAL PRIMARY KEY,
    company_id   BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    filename     TEXT NOT NULL,
    doc_type     TEXT,                              -- financials | contract | board_deck | other
    storage_path TEXT,
    status       TEXT NOT NULL DEFAULT 'uploaded',  -- uploaded | chunked | embedded | failed
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id           BIGSERIAL PRIMARY KEY,
    document_id  BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content      TEXT NOT NULL,
    embedding    TEXT,                              -- vector literal; pgvector can replace this in production
    metadata     JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS diligence_runs (
    id                   BIGSERIAL PRIMARY KEY,
    company_id           BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    status               TEXT NOT NULL DEFAULT 'pending',  -- pending | running | completed | failed
    temporal_workflow_id TEXT,
    started_at           TIMESTAMPTZ,
    finished_at          TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS findings (
    id            BIGSERIAL PRIMARY KEY,
    run_id        BIGINT NOT NULL REFERENCES diligence_runs(id) ON DELETE CASCADE,
    company_id    BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    category      TEXT,                       -- financial | legal | operational | market
    severity      TEXT,                       -- low | medium | high
    title         TEXT NOT NULL,
    detail        TEXT,
    source_doc_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_company ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document   ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_findings_run      ON findings(run_id);