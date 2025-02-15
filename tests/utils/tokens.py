import jwt

from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.common.settings import settings
from src.utils.enums import TokenType


def create_access_token(role: str) -> dict:
    user_id = str(uuid4())
    to_encode = {"sub": user_id, "role": role, "user_agent": "Other / Other / Other"}
    datetime_now = datetime.now(timezone.utc)
    expire = datetime_now + timedelta(minutes=1)
    to_encode.update({
        "exp": expire,
        "iss": "test_service",
        "nbf": datetime_now,
        "iat": datetime_now,
        "jti": str(uuid4()),
    })
    access_token = jwt.encode(
        payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM, headers={"typ": TokenType.access}
    )
    return {"access_token": access_token, "id": user_id}
