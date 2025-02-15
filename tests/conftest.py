from fastapi.testclient import TestClient
from asyncio import new_event_loop, get_running_loop
import pytest
from alembic import command
from alembic.config import Config

from sqlalchemy import text
from src.common.settings import ROOT_DIR, settings
from src.db.connector import AsyncSession
from src.main import app
from src.utils.enums import UserRole
from tests.utils.tokens import create_access_token


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = get_running_loop()
    except RuntimeError:
        loop = new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def apply_migrations():
    assert settings.TEST_DB_SCHEMA_PREFIX in settings.DB_SCHEMA, "An attempt to use a non-test scheme."

    alembic_cfg = Config(str(ROOT_DIR / "src/alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(ROOT_DIR / "src/migrations"))

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")

    async with AsyncSession() as session:
        await session.execute(text(f"DROP SCHEMA IF EXISTS {settings.DB_SCHEMA} CASCADE;"))
        await session.commit()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def user_data() -> dict:
    return create_access_token(UserRole.user)


@pytest.fixture
def executor_data() -> dict:
    return create_access_token(UserRole.executor)
