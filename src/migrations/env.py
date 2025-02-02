import sqlalchemy as sa
from alembic import context

from src.common.settings import settings
from src.db.connector import DatabaseConnector
from src.db.declarative import EXCLUDE_TABLES
from src.db.tables.base import BaseModel

config = context.config

target_metadata = BaseModel.metadata
config.set_main_option("sqlalchemy.url", settings.get_db_url(async_mode=False))


def include_object(object, name, type_, reflected, compare_to):
    """Включать в миграцию те или иные сущности БД, или нет."""
    if type_ == "table" and name in EXCLUDE_TABLES:
        return False
    return True


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
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    def include_name(name, type_, parent_names):
        if type_ == "schema":
            return name in [target_metadata.schema]
        else:
            return True

    migration_engine = DatabaseConnector.get_engine()

    with migration_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=target_metadata.schema,
            include_name=include_name,
            include_object=include_object,
        )
        connection.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA};"))
        connection.execute(sa.text('set search_path to "{}", public'.format(settings.DB_SCHEMA)))

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
