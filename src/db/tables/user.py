"""User tables."""

from sqlalchemy import Column, String, UUID, ForeignKey, Enum, Text

from src.common.settings import settings
from src.db.tables.base import BaseModel, CreatedAtMixin, IdMixin, UpdatedAtMixin
from src.utils.enums import UserRole


class User(BaseModel, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "users"

    name = Column(String(30), nullable=False, comment="Username")
    surname = Column(String(30), nullable=False, comment="User surname")
    login = Column(String(30), unique=True, nullable=False, comment="User login")
    email = Column(String(50),  unique=True, nullable=False, comment="User email")
    hashed_pwd = Column(Text, nullable=False, comment="User hashed password")
    role = Column(Enum(UserRole), nullable=False, comment="User role")


class Token(BaseModel, CreatedAtMixin):
    __tablename__ = "tokens"

    jti = Column(UUID, primary_key=True, comment="JWT identifier")
    subject = Column(
        UUID, ForeignKey(f"{settings.DB_SCHEMA}.users.id", ondelete="CASCADE"), nullable=False, comment="User"
    )
    user_agent = Column(String(100), nullable=False, comment="User device description")
