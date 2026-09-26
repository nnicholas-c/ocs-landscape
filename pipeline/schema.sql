-- Single source of truth for the curated database (data/db/papers.sqlite).
-- Add a column here before using it anywhere else.
-- paper_id is the OpenAlex work ID (like W2741809807) when known, otherwise "arxiv:<id>".

CREATE TABLE IF NOT EXISTS papers (
    paper_id        TEXT PRIMARY KEY,
    openalex_id     TEXT,
    arxiv_id        TEXT,               -- without version suffix, e.g. 2208.10041
    doi             TEXT,               -- lowercase, no https://doi.org/ prefix
    title           TEXT NOT NULL,
    abstract        TEXT,
    year            INTEGER,
    venue           TEXT,               -- journal or conference display name, or "arXiv"
    sources         TEXT NOT NULL,      -- comma-separated: openalex, arxiv, openalex_snowball
    cited_by_count  INTEGER,            -- from OpenAlex only; NULL for arXiv-only records
    relevance_score INTEGER,            -- 0..3 from stage 1b
    core_set        INTEGER DEFAULT 0,  -- 1 if in the core technical set
    extended_set    INTEGER DEFAULT 0,  -- 1 if in the team-map set (core + adjacent)
    url             TEXT,
    fetched_at      TEXT
);

CREATE TABLE IF NOT EXISTS authors (
    author_id           TEXT PRIMARY KEY,   -- OpenAlex author ID when known, else "name:<name_key>"
    display_name        TEXT NOT NULL,
    name_key            TEXT NOT NULL,      -- lowercase, accents stripped, "surname firstinitial"
    openalex_author_id  TEXT
);

CREATE TABLE IF NOT EXISTS institutions (
    inst_id             TEXT PRIMARY KEY,   -- OpenAlex institution ID when known, else "name:<key>"
    display_name        TEXT NOT NULL,
    openalex_inst_id    TEXT,
    country             TEXT
);

CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id    TEXT NOT NULL,
    author_id   TEXT NOT NULL,
    position    INTEGER,       -- 0 = first author
    inst_id     TEXT,          -- affiliation on this paper, NULL if unknown (all arXiv-only records)
    PRIMARY KEY (paper_id, author_id)
);

CREATE TABLE IF NOT EXISTS tags (
    paper_id            TEXT PRIMARY KEY,
    tech_route          TEXT,   -- values listed in the ocs-domain skill
    tech_route_secondary TEXT,
    integration         TEXT,   -- free_space_bulk, integrated_photonic, mechanical_fiber, unclear
    trl_band            TEXT,   -- lab, pilot, production, unclear
    ai_dc_fit           TEXT,   -- direct, indirect, none, unclear
    adjacent_field      TEXT,   -- values listed in the ocs-domain skill, or NULL
    evidence_span       TEXT,   -- verbatim sentence from the abstract that supports tech_route
    confidence          TEXT,   -- high, medium, low
    tagged_at           TEXT
);

CREATE TABLE IF NOT EXISTS paper_references (
    paper_id            TEXT NOT NULL,
    referenced_openalex_id TEXT NOT NULL,
    PRIMARY KEY (paper_id, referenced_openalex_id)
);

-- Which raw records were folded into which paper, and how. Lets the auditor trace every merge.
CREATE TABLE IF NOT EXISTS duplicates (
    record_key      TEXT PRIMARY KEY,   -- from the raw JSONL
    paper_id        TEXT NOT NULL,
    match_method    TEXT NOT NULL       -- canonical, doi, arxiv_id, fuzzy_title
);

CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_papers_arxiv ON papers(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_paper_authors_author ON paper_authors(author_id);
CREATE INDEX IF NOT EXISTS idx_paper_authors_inst ON paper_authors(inst_id);
