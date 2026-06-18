import os
from logging.config import fileConfig

import sqlalchemy
from alembic.runtime.environment import CompareType, CompareServerDefault
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from app.models.user import UserORM
from app.models.tag import TagORM
from app.models.category import CategoryORM
from app.models.post import PostORM

from alembic import context

from app.core.db import DATABASE_URL, Base
from app.models import UserORM

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


load_dotenv()
#DATABASE_URL = os.getenv("DATABASE_URL")

raw_url = os.environ["DATABASE_URL"]

url = raw_url

if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://"):]

elif url.startswith("postgresql://") and "+psycopg" not in url:
    url = "postgresql+psycopg://" + url[len("postgresql://"):]

DATABASE_URL = url

target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        CompareType=True,
        CompareServerDefault=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True, compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
