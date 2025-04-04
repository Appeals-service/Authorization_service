import sys
from pathlib import Path
from uuid import uuid4

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    SERVICE_NAME: str = "AS Authorization service"

    DB_USER: str = "POSTGRES"
    DB_PASSWORD: str = "POSTGRES"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "POSTGRES"
    DB_SCHEMA: str = "authorization_service"

    TEST_DB_SCHEMA_PREFIX: str = "test_"

    DEBUG: bool = True
    RELOAD: bool = True
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8001
    CORS_ORIGINS: str = "*"

    ECHO: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    SECRET_KEY: str = ""
    ALGORITHM: str = ""

    LOGGING_LEVEL: str = "DEBUG"
    LOGGING_JSON: bool = True
    LOGGING_FORMAT: str = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="allow")

    @property
    def log_config(self) -> dict:
        return {
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": self.LOGGING_LEVEL, "propagate": False},
                "sqlalchemy": {"handlers": ["default"], "level": self.LOGGING_LEVEL, "propagate": False},
            }
        }

    def get_db_url(self, async_mode: bool = True) -> str:
        return (f"{'postgresql+asyncpg' if async_mode else 'postgresql'}://"
                f"{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()

if "pytest" in sys.modules:  # pragma: no cover
    settings.DB_SCHEMA = settings.TEST_DB_SCHEMA_PREFIX + uuid4().hex + "_" + settings.DB_SCHEMA
    settings.SECRET_KEY = "test_secret_key_lksdf3"
    settings.ALGORITHM = "HS256"

    settings.DB_USER = "postgres"
    settings.DB_PASSWORD = "postgres"
    settings.DB_HOST = "localhost"
    settings.DB_PORT = 5432
    settings.DB_NAME = "postgres"
