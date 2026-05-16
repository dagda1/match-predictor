import os
from pathlib import Path

import boto3
import psycopg2

SQL_DIR = Path(__file__).parent / "sql"


def handler(event, context):
    if event.get("RequestType") == "Delete":
        return {"PhysicalResourceId": "bootstrap"}

    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    dbname = os.environ["DB_NAME"]

    rds_client = boto3.client("rds")
    token = rds_client.generate_db_auth_token(
        DBHostname=host,
        Port=5432,
        DBUsername=user,
    )

    connection = psycopg2.connect(
        host=host,
        port=5432,
        dbname=dbname,
        user=user,
        password=token,
        sslmode="verify-full",
        sslrootcert="/var/task/rds-ca-bundle.pem",
    )
    connection.autocommit = True

    execute_sql_file(connection, "bootstrap.sql")
    execute_sql_file(connection, "aws-iam.sql")
    connection.close()

    return {"PhysicalResourceId": "bootstrap"}


def execute_sql_file(connection, filename):
    sql_text = (SQL_DIR / filename).read_text()
    cursor = connection.cursor()
    cursor.execute(sql_text)
    cursor.close()
