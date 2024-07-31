import os
import json
import psycopg2
import re

from psycopg2 import sql
from typing import Optional

import data_models

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


@with_connection
def insert_paper_n_references(conn, paper: data_models.Papers, references: list[data_models.References]) -> None:
  insert_papers_query = sql.SQL('''INSERT INTO papers (paper_url, title, authors, abstract, sections_text, sections_json) VALUES (%s, %s, %s, %s, %s, %s)''')
  paper_item = (
    str(paper.paper_url),
    paper.title,
    paper.authors,
    paper.abstract,
    paper.sections_text,
    paper.sections_json,
  )

  # references query
  keys_to_add = ('referred_by_paper_url', 'reference_id', 'referred_sections', 'title', 'authors', 'journal', 'year')
  insert_references_query = f'INSERT INTO references_table ({", ".join(keys_to_add)}) VALUES ({", ".join(["%s"] * len(keys_to_add))})'
  reference_items = [
    (ref.referred_by_paper_url, ref.reference_id, ref.referred_sections, ref.title, ref.authors, ref.journal, ref.year)
    for ref in references
  ]

  # execute
  with conn.cursor() as cur:
    cur.execute(insert_papers_query, paper_item)
    cur.executemany(sql.SQL(insert_references_query), reference_items)


@with_connection
def insert_paper_ref_embeddings(conn, paper: data_models.Papers, references: list[data_models.References], embeddings: list[data_models.EmbeddingsIn]) -> None:
  # papers query
  insert_papers_query = sql.SQL('''INSERT INTO papers (paper_url, title, authors, abstract, sections_text, sections_json) VALUES (%s, %s, %s, %s, %s, %s)''')
  paper_item = (
    str(paper.paper_url),
    paper.title,
    paper.authors,
    paper.abstract,
    paper.sections_text,
    paper.sections_json,
  )

  # references query
  keys_to_add = ('referred_by_paper_url', 'reference_id', 'referred_sections', 'title', 'authors', 'journal', 'year')
  insert_references_query = f'INSERT INTO references_table ({", ".join(keys_to_add)}) VALUES ({", ".join(["%s"] * len(keys_to_add))})'
  reference_items = [
    (ref.referred_by_paper_url, ref.reference_id, ref.referred_sections, ref.title, ref.authors, ref.journal, ref.year)
    for ref in references
  ]

  # embeddings query
  insert_embeddings_query = sql.SQL('''INSERT INTO embeddings_table (paper_url, chunk, embedding) VALUES (%s, %s, %s)''')
  embedding_items = [(str(x.paper_url), x.chunk, x.embedding) for x in embeddings]

  # execute
  with conn.cursor() as cur:
    cur.execute(insert_papers_query, paper_item)
    cur.executemany(sql.SQL(insert_references_query), reference_items)
    cur.executemany(insert_embeddings_query, embedding_items)

# ===
# Papers Table
# ===

# insertion
@with_connection
def insert_paper(conn, paper: data_models.Papers) -> None:
  insert_papers_query = sql.SQL('''INSERT INTO papers (paper_url, title, authors, abstract, sections_text, sections_json) VALUES (%s, %s, %s, %s, %s, %s)''')
  item = (
    str(paper.paper_url),
    paper.title,
    paper.authors,
    paper.abstract,
    paper.sections_text,
    paper.sections_json,
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
    SELECT paper_url, title, authors, abstract, sections_text, sections_json, summary_markdown, code 
    FROM papers WHERE paper_url = %s
  ''')
  item = (paper_url, )
  with conn.cursor() as cur:
    cur.execute(read_paper_query, item)
    paper = cur.fetchone()
  if paper: return data_models.Papers(*paper)
  return None

# search paper by title

@with_connection
def search_paper_by_title(conn, query_title: str) -> Optional[data_models.SearchResult]:
  search_query = sql.SQL('SELECT paper_url, title, authors FROM papers WHERE fts @@ TO_TSQUERY(%s)')
  query_title = re.sub(r'\W+', '', query_title)
  query_title = '+'.join(query_title.split(' '))
  item = (query_title, )
  with conn.cursor() as cur:
    cur.execute(search_query, item)
    result = cur.fetchone()

  if result: return data_models.SearchResult(*result)
  return None



# ===
# References
# ===

# insertion
@with_connection
def insert_batch_references(conn, references: list[data_models.References]) -> None:
  keys_to_add = ('referred_by_paper_url', 'reference_id', 'referred_sections', 'title', 'authors', 'journal', 'year')
  insert_query = f'INSERT INTO references_table ({", ".join(keys_to_add)}) VALUES ({", ".join(["%s"] * len(keys_to_add))})'

  items = [
    (ref.referred_by_paper_url, ref.reference_id, ref.referred_sections, ref.title, ref.authors, ref.journal, ref.year)
    for ref in references
  ]
  with conn.cursor() as cur: cur.executemany(sql.SQL(insert_query), items)


@with_connection
def insert_reference_info(conn, referred_by_url: str, ref_id: str, ref_url: str, q1_ans: str, q2_ans: str, q3_ans: str):
  update_query = sql.SQL('''
    UPDATE references_table 
    SET referred_paper_url = %s, q1_answer = %s, q2_answer = %s, q3_answer = %s 
    WHERE referred_by_paper_url = %s AND reference_id = %s
  ''')
  item = [ref_url, q1_ans, q2_ans, q3_ans, referred_by_url, ref_id]
  with conn.cursor() as cur: cur.execute(update_query, item)


@with_connection
def get_reference_ids_of_paper(conn, referred_by_paper_url: str):
  read_query = sql.SQL('''
    SELECT reference_ids
    FROM references_table
    WHERE referred_by_paper_url = %s
  ''')
  item = (referred_by_paper_url, )
  with conn.cursor() as cur:
    cur.execute(read_query, item)
    result = cur.fetchall()

  if result is None or len(result) == 0: return None
  return result


@with_connection
def get_reference_info_for_searching(conn, referred_by_paper_url, reference_id: str) -> data_models.RefInfoOut:
  read_query = sql.SQL('''
    SELECT title, authors, journal, year, referred_sections
    FROM references_table
    WHERE
      referred_by_paper_url = %s
      AND reference_id = %s
    ;
  ''')
  item = (referred_by_paper_url, reference_id)
  with conn.cursor() as cur:
    cur.execute(read_query, item)
    res = cur.fetchone()

  return data_models.RefInfoOut(
    title=res[0],
    authors = [x.strip() for x in res[1].split('; ') if x.strip()] if res[1] else None,
    journal = res[2] if res[2] else None,
    year = res[3] if res[3] else None,
    referred_sections=json.loads(res[4]),
  )
    

@with_connection
def get_processed_reference(conn, paper_url: str, ref_id: str) -> Optional[data_models.ProcessRefOut]:
  read_query = sql.SQL('''
    SELECT referred_paper_url, q1_answer, q2_answer, q3_answer
    FROM references_table
    WHERE referred_by_paper_url = %s AND reference_id = %s
    ;
  ''')
  item = (paper_url, ref_id)
  with conn.cursor() as cur:
    cur.execute(read_query, item)
    result = cur.fetchone()
  if not result or None in result: return None
  return data_models.ProcessRefOut(*result)


@with_connection
def get_reference_urls(conn, paper_url: str) -> Optional[list[str]]:
  query = sql.SQL('''SELECT referred_paper_url FROM references_table WHERE referred_by_paper_url = %s;''')
  item = (paper_url, )
  with conn.cursor() as cur:
    cur.execute(query, item)
    return cur.fetchall()


# ===
# Embeddings
# ===
@with_connection
def insert_batch_embeddings(conn, embds: list[data_models.EmbeddingsIn]):
  insert_query = sql.SQL('''INSERT INTO embeddings_table (paper_url, chunk, embedding) VALUES (%s, %s, %s)''')
  items = [(str(x.paper_url), x.chunk, x.embedding) for x in embds]
  with conn.cursor() as cur: cur.executemany(insert_query, items)

@with_connection
def get_top_k_similar(conn, query_embedding: list[float], paper_urls: list[str], k: int) -> list[data_models.EmbeddingsOut]:
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

  return [data_models.EmbeddingsOut(paper_url=res[0], chunk=res[1], sim_score=res[2]) for res in results]




if __name__ == '__main__':
  create_tables()
