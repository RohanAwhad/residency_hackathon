CREATE EXTENSION IF NOT EXISTS VECTOR;

CREATE TABLE IF NOT EXISTS papers (
  paper_url TEXT PRIMARY KEY,
  title TEXT,
  abstract TEXT,
  sections TEXT, --json str
  summary_markdown TEXT,
  code TEXT
);

CREATE TABLE IF NOT EXISTS references_table (
  id SERIAL PRIMARY KEY,
  curr_paper_url TEXT,
  ref_paper_url TEXT,
  q1 TEXT,
  q2 TEXT,
  q3 TEXT,
  CONSTRAINT fk_curr_paper FOREIGN KEY (curr_paper_url) REFERENCES papers(paper_url),
  CONSTRAINT fk_ref_paper FOREIGN KEY (ref_paper_url) REFERENCES papers(paper_url),
  UNIQUE (curr_paper_url, ref_paper_url)
);


CREATE TABLE IF NOT EXISTS embeddings_table (
  id SERIAL PRIMARY KEY,
  paper_url TEXT,
  chunk TEXT,
  embedding VECTOR(384),
  CONSTRAINT fk_paper FOREIGN KEY (paper_url) REFERENCES papers(paper_url)
);

-- I need to create tables for user and chat session
