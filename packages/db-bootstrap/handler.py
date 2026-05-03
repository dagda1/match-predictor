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

    execute_sql_file(connection, "bootstrap.sql")
    execute_sql_file(connection, "aws-iam.sql")
    connection.close()

    return {"PhysicalResourceId": "bootstrap"}


def execute_sql_file(connection, filename):
    sql_text = (SQL_DIR / filename).read_text()
    cursor = connection.cursor()
    cursor.execute(sql_text)
    cursor.close()
