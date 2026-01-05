# wait_for_db.py
import os
import time
import psycopg2

db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")

while True:
    try:
        conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_pass, host=db_host
        )
        conn.close()
        print("DB is ready!")
        break
    except psycopg2.OperationalError:
        print("Waiting for DB...")
        time.sleep(2)
