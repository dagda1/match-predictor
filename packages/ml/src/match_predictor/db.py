import os
from pathlib import Path

import boto3
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

CA_BUNDLE_PATH = Path(__file__).resolve().parent.parent / "rds-ca-bundle.pem"


def _resolve_password(host: str, user: str) -> str:
    password = os.environ.get("DB_PASSWORD")
    if password is not None:
        return password

    region = os.environ.get("DB_REGION", "us-west-2")
    rds = boto3.client("rds", region_name=region)
    return rds.generate_db_auth_token(
        DBHostname=host,
        Port=5432,
        DBUsername=user,
    )


def _ssl_connect_args(sslmode: str) -> dict:
    if sslmode == "disable":
        return {"sslmode": "disable"}

    return {
        "sslmode": "verify-full",
        "sslrootcert": str(CA_BUNDLE_PATH),
    }


def create_db_engine() -> Engine:
    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    dbname = os.environ["DB_NAME"]
    password = _resolve_password(host, user)
    sslmode = os.environ.get("DB_SSLMODE", "require")

    connect_args = {
        "host": host,
        "user": user,
        "password": password,
        "dbname": dbname,
        "port": 5432,
        **_ssl_connect_args(sslmode),
    }

    return create_engine(
        "postgresql+psycopg2://",
        poolclass=NullPool,
        connect_args=connect_args,
    )
