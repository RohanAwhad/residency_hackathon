import os
import psycopg2

from db_models import Paper

# Connect to the database
PG_USER = os.environ['PG_USER']
PG_PASSWORD = os.environ['PG_PASSWORD']
PG_HOST = os.environ['PG_HOST']
PG_PORT = os.environ['PG_PORT']
PG_DB = os.environ['PG_DB']

def with_connection(func):
  """
  Function decorator for passing connections
  """
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
def insert_paper(conn, paper: Paper): pass

@with_connection
def insert_batch_papers(conn, papers: list[Paper]): pass



if __name__ == '__main__':
  create_tables()