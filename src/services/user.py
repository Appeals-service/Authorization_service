"""User service."""
from uuid import uuid4

from pydantic import validate_email
from pydantic_core import PydanticCustomError
from fastapi import status, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from user_agents import parse

from common.settings import settings
from db.connector import AsyncSession
from db.tables import User
from dto.schemas.users import UserCreate, UserAuth, RefreshToken
from repositories.users import UsersRepository
from utils.auth import get_hashed_pwd, create_tokens, verify_pwd, check_token_type, get_refresh_token_payload
from utils.enums import UserRole, TokenType


class UserService:

    @classmethod
    async def register(cls, user_data: UserCreate) -> dict:

        user_id = await cls._add_user(user_data)
        access_token, refresh_token = await cls._get_tokens(user_id, user_data.role, str(parse(user_data.user_agent)))

        return dict(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    async def login(cls, user_data: UserAuth) -> dict:

        is_email = True
        try:
            validate_email(user_data.login_or_email)
            user_data.login_or_email = user_data.login_or_email.lower()
        except PydanticCustomError:
            is_email = False

        async with AsyncSession() as session:
            user_data_from_db = await UsersRepository.get_user_data(
                session, user_data.login_or_email, "email" if is_email else "login"
            )

        if not user_data_from_db or not verify_pwd(user_data.pwd, user_data_from_db.hashed_pwd):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unauthorized")

        access_token, refresh_token = await cls._get_tokens(
            user_data_from_db.id, user_data_from_db.role, str(parse(user_data.user_agent))
        )
        return dict(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def logout(user: User, user_agent: str) -> None:
        async with AsyncSession() as session:
            await UsersRepository.delete_refresh_token_by_user_data(session, user.id, str(parse(user_agent)))
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

    @classmethod
    async def refresh(cls, refresh_token: RefreshToken, user_agent, response: Response) -> dict:
        user_agent = str(parse(user_agent))
        check_token_type(refresh_token.refresh_token, TokenType.refresh)

        payload = await get_refresh_token_payload(refresh_token.refresh_token)

        async with AsyncSession() as session:
            if (
                    not (token_data_from_db := await UsersRepository.get_token_data_by_jti(session, payload.get("jti")))
                    or user_agent != token_data_from_db.user_agent
            ):
                await UsersRepository.delete_tokens_by_user_id(session, payload.get("sub"))
                await session.commit()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid token")

            await UsersRepository.delete_refresh_token_by_jti(session, payload.get("jti"))
            await session.commit()

        access_token, refresh_token = await cls._get_tokens(payload.get("sub"), payload.get("role"), user_agent)

        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return dict(refresh_token=refresh_token)

    @staticmethod
    async def _add_user(user_data: UserCreate) -> uuid4:
        user_data.pwd = get_hashed_pwd(user_data.pwd)

        async with AsyncSession() as session:
            user_id = await UsersRepository.insert_user_data(
                session, user_data.model_dump(by_alias=True, exclude={"user_agent"})
            )
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args[0].split('DETAIL:')[1]}")

        return user_id

    @staticmethod
    async def _get_tokens(user_id: uuid4, role: UserRole | str, user_agent: str) -> tuple[str, str]:

        token_data = {"sub": str(user_id), "role": role, "user_agent": user_agent}
        access_token, refresh_token, refresh_jti = create_tokens(
            token_data, settings.ACCESS_TOKEN_EXPIRE_MINUTES, settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

        async with AsyncSession() as session:
            await UsersRepository.insert_refresh_token_data(
                session, {"jti": refresh_jti, "subject": user_id, "user_agent": user_agent}
            )
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args[0].split('DETAIL:')[1]}")

        return access_token, refresh_token
