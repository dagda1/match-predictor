import os
import subprocess
from urllib.parse import quote_plus

import boto3


def handler(event, context):
    physical_id = event.get("PhysicalResourceId", "migration")

    if event.get("RequestType") == "Delete":
        return {"PhysicalResourceId": physical_id}

    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    dbname = os.environ["DB_NAME"]

    rds_client = boto3.client("rds")
    token = rds_client.generate_db_auth_token(
        DBHostname=host,
        Port=5432,
        DBUsername=user,
    )

    encoded_token = quote_plus(token)
    os.environ["DATABASE_URL"] = (
        f"postgresql+psycopg2://{user}:{encoded_token}"
        f"@{host}:5432/{dbname}?sslmode=require"
    )

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd="/var/task",
        capture_output=True,
        text=True,
    )

    print("alembic stdout:", result.stdout)
    print("alembic stderr:", result.stderr)

    if result.returncode != 0:
        trimmed = (result.stderr or "")[-400:]
        raise RuntimeError(f"alembic exit {result.returncode}: {trimmed}")

    return {"PhysicalResourceId": physical_id}
