from uuid import uuid4

from sqlalchemy import select, delete, and_
from sqlalchemy.engine.row import Row

from db.connector import AsyncSession
from db.tables import User, Token


class UsersRepository:

    @staticmethod
    async def insert_user_data(session: AsyncSession, user_data: dict) -> uuid4:
        user_id = uuid4()
        user = User(id=user_id, **user_data)
        session.add(user)
        return user_id

    @staticmethod
    async def insert_refresh_token_data(session: AsyncSession, token_data: dict) -> None:
        token = Token(**token_data)
        session.add(token)

    @staticmethod
    async def get_user_data(session: AsyncSession, value: str, column_name: str) -> Row | None:
        query = select(User.id, User.hashed_pwd, User.role).where(getattr(User, column_name) == value)
        result = await session.execute(query)
        return result.one_or_none()

    @staticmethod
    async def get_user(session: AsyncSession, user_id: str) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def delete_refresh_token_by_user_data(session: AsyncSession, user_id: str, user_agent: str) -> None:
        query = delete(Token).where(and_(Token.subject == user_id, Token.user_agent == user_agent))
        await session.execute(query)

    @staticmethod
    async def delete_refresh_token_by_jti(session: AsyncSession, jti: str) -> None:
        query = delete(Token).where(Token.jti == jti)
        await session.execute(query)

    @staticmethod
    async def get_token_data_by_jti(session: AsyncSession, jti: str) -> Row:
        query = select(Token.subject, Token.user_agent).where(Token.jti == jti)
        result = await session.execute(query)
        return result.one_or_none()

    @staticmethod
    async def delete_tokens_by_user_id(session: AsyncSession, user_id: str) -> None:
        query = delete(Token).where(Token.subject == user_id)
        await session.execute(query)

    @classmethod
    async def delete_user_by_user_id(cls, session: AsyncSession, user_id: str) -> None:
        query = delete(User).where(User.id == user_id)
        await session.execute(query)
