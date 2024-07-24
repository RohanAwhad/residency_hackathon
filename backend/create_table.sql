CREATE EXTENSION IF NOT EXISTS VECTOR;

CREATE TABLE IF NOT EXISTS papers (
  paper_url TEXT PRIMARY KEY,
  title TEXT,
  authors TEXT,
  abstract TEXT,
  sections TEXT, --json str
  summary_markdown TEXT,
  code TEXT
);

CREATE TABLE IF NOT EXISTS references_table (
  id SERIAL PRIMARY KEY,
  referred_by_paper_url TEXT,
  referred_paper_url TEXT,
  q1_answer TEXT,
  q2_answer TEXT,
  q3_answer TEXT,
  CONSTRAINT fk_curr_paper FOREIGN KEY (referred_by_paper_url) REFERENCES papers(paper_url),
  CONSTRAINT fk_ref_paper FOREIGN KEY (referred_paper_url) REFERENCES papers(paper_url),
  UNIQUE (referred_by_paper_url, referred_paper_url)
);


CREATE TABLE IF NOT EXISTS embeddings_table (
  id SERIAL PRIMARY KEY,
  paper_url TEXT,
  chunk TEXT,
  embedding VECTOR(384),
  CONSTRAINT fk_paper FOREIGN KEY (paper_url) REFERENCES papers(paper_url)
);

-- I need to create tables for user and chat session
