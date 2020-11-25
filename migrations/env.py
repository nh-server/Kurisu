from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from configparser import ConfigParser

import os
import sys
from utils.models import db

IS_DOCKER = os.environ.get('IS_DOCKER', 0)
if IS_DOCKER:
    def get_env(name: str):
        contents = os.environ.get(name)
        if contents is None:
            contents_file = os.environ.get(name + '_FILE')
            try:
                with open(contents_file, 'r', encoding='utf-8') as f:
                    contents = f.readline().strip()
            except FileNotFoundError:
                sys.exit(f"Couldn't find environment variables {name} or {name}_FILE.")

        return contents

    db_user = get_env('DB_USER')
    db_password = get_env('DB_PASSWORD')
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@db/{db_user}"
else:
    configparser = ConfigParser()
    configparser.read("data/config.ini")
    DATABASE_URL = configparser['Main']['database_url']

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_URL)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
