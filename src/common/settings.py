from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    SERVICE_NAME: str = "AS Authorization service"

    DEBUG: bool = True
    RELOAD: bool = True
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8001
    CORS_ORIGINS: str = "*"

    DB_USER: str = "POSTGRES"
    DB_PASSWORD: str = "POSTGRES"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "POSTGRES"
    DB_SCHEMA: str = "authorization_service"

    ECHO: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    SECRET_KEY: str = "feisom_ob_teibl_rt54uyjhn67rtgfvbrtr_nyuumn"
    ALGORITHM: str = "HS256"

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
