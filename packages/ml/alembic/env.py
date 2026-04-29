import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from match_predictor.db_models import Base

config = context.config

target_metadata = Base.metadata


def build_connectable():
    if "DB_PASSWORD" in os.environ:
        return create_engine(
            "postgresql+psycopg2://",
            poolclass=pool.NullPool,
            connect_args={
                "host": os.environ["DB_HOST"],
                "user": os.environ["DB_USER"],
                "password": os.environ["DB_PASSWORD"],
                "dbname": os.environ["DB_NAME"],
                "sslmode": os.environ.get("DB_SSLMODE", "require"),
                "port": 5432,
            },
        )

    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    return engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


def run_migrations_offline() -> None:
    url = os.environ["DATABASE_URL"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = build_connectable()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
