import os
import json
from pathlib import Path

import boto3
import psycopg2

SQL_DIR = Path(__file__).parent / "sql"


def handler(event, context):
    if event.get("RequestType") == "Delete":
        return {"PhysicalResourceId": "bootstrap"}

    secrets = boto3.client("secretsmanager")
    credentials = json.loads(
        secrets.get_secret_value(SecretId=os.environ["SECRET_ARN"])["SecretString"]
    )

    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=credentials["username"],
        password=credentials["password"],
    )
    connection.autocommit = True

    try:
        execute_sql_file(connection, "bootstrap.sql")
        execute_sql_file(connection, "aws-iam.sql")
    finally:
        connection.close()

    return {"PhysicalResourceId": "bootstrap"}


def execute_sql_file(connection, filename):
    sql_text = (SQL_DIR / filename).read_text()
    with connection.cursor() as cursor:
        cursor.execute(sql_text)
