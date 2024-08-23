CREATE EXTENSION IF NOT EXISTS VECTOR;

CREATE TABLE IF NOT EXISTS users_table (
  user_id VARCHAR(255) PRIMARY KEY,
  given_name VARCHAR(255) NOT NULL,
  family_name VARCHAR(255) NOT NULL,
  email_id VARCHAR(255) UNIQUE NOT NULL,
  google_access_token VARCHAR(255),
  google_refresh_token VARCHAR(255),
  google_id_token VARCHAR(255),
  profile_pic VARCHAR(255),
  api_key VARCHAR(255) UNIQUE NOT NULL
);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS papers (
  paper_url TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  authors TEXT NOT NULL,
  abstract TEXT,
  sections_text TEXT, --json str
  sections_json TEXT,
  summary_markdown TEXT,
  code TEXT,
  fts TSVECTOR GENERATED ALWAYS AS (TO_TSVECTOR('english', TRIM(LOWER(title)))) STORED
);

-- I am getting error here. Iam using Postgres with pgvector extension


CREATE INDEX title_fts ON papers USING GIN (fts);


CREATE TABLE IF NOT EXISTS references_table (
  id SERIAL PRIMARY KEY,
  referred_by_paper_url TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  referred_sections TEXT NOT NULL,

  title TEXT NOT NULL,
  authors TEXT,
  journal TEXT,
  year TEXT,

  referred_paper_url TEXT,
  q1_answer TEXT,
  q2_answer TEXT,
  q3_answer TEXT,
  CONSTRAINT fk_curr_paper FOREIGN KEY (referred_by_paper_url) REFERENCES papers(paper_url),
  CONSTRAINT fk_ref_paper FOREIGN KEY (referred_paper_url) REFERENCES papers(paper_url)
  -- UNIQUE (referred_by_paper_url, referred_paper_url) Will Add it later when finalized
);


CREATE TABLE IF NOT EXISTS embeddings_table (
  id SERIAL PRIMARY KEY,
  paper_url TEXT,
  chunk TEXT,
  embedding VECTOR(384),
  CONSTRAINT fk_paper FOREIGN KEY (paper_url) REFERENCES papers(paper_url)
);

-- I need to create tables for user and chat session
