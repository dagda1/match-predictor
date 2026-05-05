import os
from pathlib import Path

import boto3
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

CA_BUNDLE_PATH = Path(__file__).resolve().parent.parent / "rds-ca-bundle.pem"

_rds_client = None


def _get_rds_client():
    global _rds_client
    if _rds_client is None:
        region = os.environ.get("DB_REGION", "us-west-2")
        _rds_client = boto3.client("rds", region_name=region)
    return _rds_client


def _generate_iam_token(host: str, user: str) -> str:
    return _get_rds_client().generate_db_auth_token(
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
    if "DATABASE_URL" in os.environ:
        return create_engine(os.environ["DATABASE_URL"], poolclass=NullPool)

    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    dbname = os.environ["DB_NAME"]
    sslmode = os.environ.get("DB_SSLMODE", "require")
    static_password = os.environ.get("DB_PASSWORD")

    connect_args = {
        "host": host,
        "user": user,
        "dbname": dbname,
        "port": 5432,
        **_ssl_connect_args(sslmode),
    }

    if static_password is not None:
        connect_args["password"] = static_password

    engine = create_engine(
        "postgresql+psycopg2://",
        poolclass=NullPool,
        connect_args=connect_args,
    )

    if static_password is None:
        @event.listens_for(engine, "do_connect")
        def _refresh_iam_token(_dialect, _conn_rec, _cargs, cparams):
            cparams["password"] = _generate_iam_token(host, user)

    return engine
