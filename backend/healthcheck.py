# I want this to keep on checking if my microservices are alive.
# I have 3 services:
#   1. FastAPI server (the main backend)
#   2. GROBID server
#   3. PostGres server


import requests
import time
import threading
import os


STOP_FLAG = threading.Event()


def check_fastapi(secs):
    while not STOP_FLAG.is_set():
        try:
            res = requests.get("http://api.refexplorer.com/healthcheck")
            if res.status_code != 200:
                print("FastAPI server is down")
                # TODO: (rohan) send telegram message
            time.sleep(secs)

        except Exception as e:
            print("While running FastAPI healthcheck, got the following error:", e)
            # TODO: (rohan) send telegram message

    print("Stopped FastAPI healtcheck thread")


def check_postgres(secs):
    # connect to db
    # run "select 1" cmd
    # if it returns 1, its good, else its broken
    import psycopg2

    while not STOP_FLAG.is_set():
        try:
            # Connect to the database
            PG_USER = os.environ["PG_USER"]
            PG_PASSWORD = os.environ["PG_PASSWORD"]
            PG_HOST = os.environ["PG_HOST"]
            PG_PORT = os.environ["PG_PORT"]
            PG_DB = os.environ["PG_DB"]

            conn = psycopg2.connect(
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD,
                host=PG_HOST,
                port=PG_PORT,
            )
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                if result is None or result[0] != 1:
                    print("Postgres server didn't respond with 1")
                    # TODO: (rohan) send telegram message

            time.sleep(secs)
        except Exception as e:
            print("While running Postgres healthcheck, got the following error:", e)
            # TODO: (rohan) send telegram message

    print("Stopped Postgres healtcheck thread")


def check_grobid(secs):
    while not STOP_FLAG.is_set():
        try:
            res = requests.get("http://localhost:8070/api/isalive")
            if res.status_code != 200 or res.text != "true":
                print("GROBID server didn't respond with true")
                # TODO: (rohan) send telegram message

            time.sleep(secs)
        except Exception as e:
            print("While running GROBID healthcheck, got the following error:", e)
            # TODO: (rohan) send telegram message


if __name__ == "__main__":
    # define healthcheck threads
    threads = [
        threading.Thread(target=check_fastapi, args=(10,)),
        threading.Thread(target=check_postgres, args=(30,)),
        threading.Thread(target=check_grobid, args=(10,)),
    ]

    # run healthcheck threads
    for th in threads:
        th.start()

    try:
        input("Press Ctrl-C to exit:")
    except KeyboardInterrupt as e:
        STOP_FLAG.set()
        for th in threads:
            th.join()
        print("All threads stopped")
