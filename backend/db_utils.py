import os
import psycopg2

from psycopg2 import sql

from db_models import Paper, References, Embeddings, EmbeddingsIn, EmbeddingsOut

# Connect to the database
PG_USER = os.environ['PG_USER']
PG_PASSWORD = os.environ['PG_PASSWORD']
PG_HOST = os.environ['PG_HOST']
PG_PORT = os.environ['PG_PORT']
PG_DB = os.environ['PG_DB']

def with_connection(func):
  '''
  Function decorator for passing connections
  '''
  def connection(*args, **kwargs):
    # Here, you may even use a connection pool
    conn = psycopg2.connect(dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT)
    try:
      rv = func(conn, *args, **kwargs)
    except Exception as e:
      conn.rollback()
      raise e
    else:
      # Can decide to see if you need to commit the transaction or not
      conn.commit()
    finally:
      conn.close()
    return rv
  return connection

@with_connection
def create_tables(conn):
  cur = conn.cursor()
  with open('create_table.sql', 'r') as f: cur.execute(f.read())
  cur.close()


# ===
# Papers Table
# ===

# insertion
@with_connection
def insert_paper(conn, paper: Paper):
  insert_papers_query = sql.SQL('''INSERT INTO papers (paper_url, title, authors, abstract, sections) VALUES (%s, %s, %s, %s, %s)''')
  item = (
    str(paper.paper_url),
    paper.title,
    paper.authors,
    paper.abstract,
    paper.sections,
  )
  with conn.cursor() as cur: cur.execute(insert_papers_query, item)

@with_connection
def insert_summary(conn, paper_url: str, summary: str):
  update_query = sql.SQL('''UPDATE papers SET summary_markdown = %s WHERE paper_url = %s''')
  item = [summary, paper_url]
  with conn.cursor() as cur: cur.execute(update_query, item)

@with_connection
def insert_code(conn, paper_url: str, code: str):
  update_query = sql.SQL('''UPDATE papers SET code = %s WHERE paper_url = %s''')
  item = [code, paper_url]
  with conn.cursor() as cur: cur.execute(update_query, item)

# read
@with_connection
def read_paper(conn, paper_url: str):
  read_paper_query = sql.SQL('''
    SELECT paper_url, title, authors, abstract, sections, summary_markdown, code 
    FROM papers WHERE paper_url = %s
  ''')
  item = (paper_url, )
  with conn.cursor() as cur:
    cur.execute(read_paper_query, item)
    paper = cur.fetchone()

  return Paper(
    paper_url = paper[0],
    title = paper[1],
    authors = paper[2],
    abstract = paper[3],
    sections = paper[4],
    summary_markdown = paper[5],
    code = paper[6],
  )


# ===
# References
# ===

# insertion
@with_connection
def insert_reference(conn, ref: References):
  insert_query = sql.SQL('''INSERT INTO references_table (referred_by_paper_url, referred_paper_url) VALUES (%s, %s)''')
  item = (str(ref.referred_by_paper_url), str(ref.referred_paper_url))
  with conn.cursor() as cur: cur.execute(insert_query, item)

@with_connection
def insert_reference_answers(conn, ref: References):
  update_query = sql.SQL('''
    UPDATE references_table 
    SET q1_answer = %s, q2_answer = %s, q3_answer = %s 
    WHERE referred_by_paper_url = %s AND referred_paper_url = %s
  ''')
  item = [ref.q1_answer, ref.q2_answer, ref.q3_answer, str(ref.referred_by_paper_url), str(ref.referred_paper_url)]
  with conn.cursor() as cur: cur.execute(update_query, item)

@with_connection
def get_references_of_paper(conn, referred_by_paper_url: str):
  read_query = sql.SQL('''
    SELECT referred_by_paper_url, referred_paper_url, q1_answer, q2_answer, q3_answer
    FROM references_table
    WHERE referred_by_paper_url = %s
  ''')
  item = (referred_by_paper_url, )
  with conn.cursor() as cur:
    cur.execute(read_query, item)
    result = cur.fetchall()

  refs = []
  for res in result:
    _ = References(
      referred_by_paper_url = res[0],
      referred_paper_url = res[1],
      q1_answer = res[2],
      q2_answer = res[3],
      q3_answer = res[4],
    )
    refs.append(_)
  return refs
    


# ===
# Embeddings
# ===
@with_connection
def insert_batch_embeddings(conn, embds: list[EmbeddingsIn]):
  insert_query = sql.SQL('''INSERT INTO embeddings_table (paper_url, chunk, embedding) VALUES (%s, %s, %s)''')
  items = [(str(x.paper_url), x.chunk, x.embedding) for x in embds]
  with conn.cursor() as cur: cur.executemany(insert_query, items)

@with_connection
def get_top_k_similar(conn, query_embedding: list[float], paper_urls: list[str], k: int) -> list[EmbeddingsOut]:
  search_query = sql.SQL('''
    SELECT paper_url, chunk, (1 - (embedding <=> VECTOR(%s::VECTOR(384)))) as sim_score
    FROM embeddings_table
    WHERE paper_url = ANY(%s)
    ORDER BY sim_score DESC
    LIMIT %s
  ''')
  item = (query_embedding, paper_urls, k)
  with conn.cursor() as cur:
    cur.execute(search_query, item)
    results = cur.fetchall()

  return [EmbeddingsOut(paper_url=res[0], chunk=res[1], sim_score=res[2]) for res in results]




if __name__ == '__main__':
  create_tables()
