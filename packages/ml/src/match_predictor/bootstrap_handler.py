import os
import json
import boto3
import psycopg2
from psycopg2 import sql


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

    migrator_user = os.environ["MIGRATOR_USER"]
    app_user = os.environ["APP_USER"]

    try:
        for username in (migrator_user, app_user):
            create_user_if_missing(connection, username)
            grant_iam_login(connection, username)

        grant_migrator_schema(connection, migrator_user)
        grant_app_privileges(connection, app_user)
    finally:
        connection.close()

    return {"PhysicalResourceId": "bootstrap"}


def create_user_if_missing(connection, username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", [username])
        if cursor.fetchone() is None:
            cursor.execute(
                sql.SQL("CREATE USER {user};").format(user=sql.Identifier(username))
            )


def grant_iam_login(connection, username):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("GRANT rds_iam TO {user};").format(user=sql.Identifier(username))
        )


def grant_migrator_schema(connection, username):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("GRANT CREATE, USAGE ON SCHEMA public TO {user};").format(
                user=sql.Identifier(username)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL ON ALL TABLES IN SCHEMA public TO {user};").format(
                user=sql.Identifier(username)
            )
        )


def grant_app_privileges(connection, username):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("GRANT USAGE ON SCHEMA public TO {user};").format(
                user=sql.Identifier(username)
            )
        )
        cursor.execute(
            sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {user};").format(
                user=sql.Identifier(username)
            )
        )
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user};").format(
                user=sql.Identifier(username)
            )
        )
