import datetime

from sqlalchemy import Column, DateTime, func, UUID

from src.db.declarative import Base


class BaseModel(Base):
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict_lower(self):
        return {str.lower(c.name): getattr(self, c.name) for c in self.__table__.columns}


class IdMixin:
    id = Column(UUID, primary_key=True, nullable=False, comment="UUID identifier")


class CreatedAtMixin:
    created_at = Column(
        DateTime,
        nullable=False,
        comment="Creation datetime",
        default=datetime.datetime.now,
        server_default=func.now(),
    )


class UpdatedAtMixin:
    updated_at = Column(
        DateTime,
        nullable=False,
        comment="Update datetime",
        default=datetime.datetime.now,
        server_default=func.now(),
        onupdate=func.now(),
    )
