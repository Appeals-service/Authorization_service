from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

from src.common.settings import settings

CONVENTION = {
    "ix": "IX_%(column_0_label)s",
    "uq": "UQ_%(table_name)s_%(column_0_name)s",
    "ck": "CK_%(table_name)s_%(constraint_name)s",
    "fk": "FK_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "PK_%(table_name)s",
}
EXCLUDE_TABLES = []
Base = declarative_base(metadata=MetaData(schema=settings.DB_SCHEMA, naming_convention=CONVENTION))
