import os
import subprocess

import boto3
import psycopg2
from psycopg2 import sql


def handler(event, context):
    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    mlflow_db = os.environ["MLFLOW_DB_NAME"]

    rds_client = boto3.client("rds")
    token = rds_client.generate_db_auth_token(
        DBHostname=host,
        Port=5432,
        DBUsername=user,
    )

    ssl_args = {
        "sslmode": "verify-full",
        "sslrootcert": "/var/task/rds-ca-bundle.pem",
    }

    conn = psycopg2.connect(
        host=host,
        port=5432,
        user=user,
        password=token,
        dbname="postgres",
        **ssl_args,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (mlflow_db,))
    if cur.fetchone() is None:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(mlflow_db)))
    cur.close()
    conn.close()

    upgrade_url = f"postgresql://{user}:{token}@{host}:5432/{mlflow_db}?sslmode=verify-full&sslrootcert=/var/task/rds-ca-bundle.pem"

    result = subprocess.run(
        ["mlflow", "db", "upgrade", upgrade_url],
        cwd="/var/task",
        capture_output=True,
        text=True,
    )

    print("mlflow stdout:", result.stdout)
    print("mlflow stderr:", result.stderr)

    if result.returncode != 0:
        trimmed = (result.stderr or "")[-400:]
        raise RuntimeError(f"mlflow db upgrade exit {result.returncode}: {trimmed}")

    return {"status": "ok"}
