from datetime import datetime, timezone, timedelta
from uuid import uuid4

import jwt
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status, Depends

from src.common.settings import settings
from src.db.connector import AsyncSession
from src.db.tables import User
from src.repositories.user import UserRepository
from src.utils.enums import TokenType

pwd_context = CryptContext(schemes=["bcrypt"])


def get_hashed_pwd(pwd: str) -> str:
    return pwd_context.hash(pwd)


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_tokens(data: dict, access_time_delta: int, refresh_time_delta: int) -> tuple[str, str, str]:
    to_encode = data.copy()
    datetime_now = datetime.now(timezone.utc)
    expire = datetime_now + timedelta(minutes=access_time_delta)
    to_encode.update({
        "exp": expire,
        "iss": settings.SERVICE_NAME,
        "nbf": datetime_now,
        "iat": datetime_now,
        "jti": str(uuid4()),
    })
    access_token = jwt.encode(
        payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM, headers={"typ": TokenType.access}
    )

    refresh_jti = str(uuid4())
    expire = datetime_now + timedelta(minutes=refresh_time_delta)
    to_encode.update({"exp": expire, "jti": refresh_jti})
    refresh_token = jwt.encode(
        payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM, headers={"typ": TokenType.refresh}
    )

    return access_token, refresh_token, refresh_jti


def get_token(request: Request) -> str:
    if not (token := request.cookies.get("access_token")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    check_token_type(token, TokenType.access)

    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not (user_id := payload.get("sub")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    async with AsyncSession() as session:
        user = await UserRepository.get_user(session, user_id)

    if not user or payload.get("role") != user.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")

    return user


def check_token_type(token: str, required_type: TokenType) -> None:
    header = jwt.get_unverified_header(token)
    if (token_type := header.get("typ")) and token_type != required_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")


async def get_refresh_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    except jwt.ExpiredSignatureError as e:
        payload = jwt.decode(
            token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False}
        )
        async with AsyncSession() as session:
            await UserRepository.delete_refresh_token_by_jti(session, payload.get("jti"))
            await session.commit()

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return payload
