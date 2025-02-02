import contextlib
import logging

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.common.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format=settings.LOGGING_FORMAT)
logger.setLevel(logging.INFO)


class DatabaseConnector:
    @staticmethod
    async def get_async_engine() -> AsyncEngine:
        return create_async_engine(
            url=settings.get_db_url(),
            echo=settings.ECHO,
            poolclass=NullPool,
        )

    @staticmethod
    def get_engine(database_schema: str | None = None) -> Engine:
        db_schema = database_schema or settings.DB_SCHEMA
        return create_engine(
            url=settings.get_db_url(async_mode=False),
            poolclass=NullPool,
            connect_args={"options": f"-csearch_path={db_schema}"},
        )

    @staticmethod
    def get_sessionmaker(
        session_engine: AsyncEngine | Engine, is_async: bool = True
    ) -> sessionmaker | async_sessionmaker:
        sessionmaker_func, session_class = (
            (async_sessionmaker, AsyncSessionType) if is_async else (sessionmaker, SessionType)
        )
        return sessionmaker_func(
            bind=session_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=session_class,
        )

    @classmethod
    @contextlib.contextmanager
    def get_sync_session(cls, schema: str | None = None) -> SessionType:
        engine = cls.get_engine(database_schema=schema)
        session = cls.get_sessionmaker(session_engine=engine, is_async=False)
        with session() as sync_session:
            try:
                yield sync_session
            finally:
                sync_session.close()

    @classmethod
    @contextlib.asynccontextmanager
    async def get_async_session(cls, schema: str | None = None) -> AsyncSessionType:
        """Асинхронный контекстный менеджер подключения к базе данных."""
        database_schema = schema or settings.DB_SCHEMA
        session_maker = cls.get_sessionmaker(session_engine=await cls.get_async_engine())

        async with session_maker() as async_session:
            try:
                conn = await async_session.connection()
                await conn.execution_options(schema_translate_map={None: database_schema})
                yield async_session
            except BaseException:
                await async_session.rollback()
                raise
            finally:
                await async_session.close()


Session = DatabaseConnector.get_sync_session
AsyncSession = DatabaseConnector.get_async_session
