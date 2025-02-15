from uuid import uuid4

import pytest
from sqlalchemy import select, insert
from fastapi import status

from src.db.connector import AsyncSession
from src.db.tables import User, Token
from src.utils.enums import UserRole
from src.utils.auth import get_hashed_pwd


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, user_agent, expected_status, expected_user_agent",
    [
        (
                "test_register_name_1",
                "test_register_surname_1",
                "test_register_login_1",
                "test_register_email_1@mail.net",
                UserRole.user,
                "test_register_pwd_1",
                "test_register_user_agent_1",
                status.HTTP_201_CREATED,
                "Other / Other / Other",
        ),
        (
                "test_register_name_2",
                "test_register_surname_2",
                "test_register_login_2",
                "test_register_email_2@mail.net",
                UserRole.executor,
                "test_register_pwd_2",
                "test_register_user_agent_2",
                status.HTTP_201_CREATED,
                "Other / Other / Other",
        ),
    ],
)
async def test_register(
        client, name, surname, login, email, role, pwd, user_agent, expected_status, expected_user_agent
):
    json = {
        "name": name,
        "surname": surname,
        "login": login,
        "email": email,
        "role": role,
        "pwd": pwd,
        "user_agent": user_agent,
    }

    response = client.post("/api/v1/users/registration", json=json)
    response_json = response.json()
    async with AsyncSession() as session:
        user_result = await session.execute(select(User).where(User.login == login))
        user_result = user_result.scalar()
        token_result = await session.execute(select(Token).where(Token.subject == user_result.id))
        token_result = token_result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("access_token") is not None
    assert response_json.get("refresh_token") is not None
    assert len(response_json) == 2
    assert user_result.name == name
    assert user_result.surname == surname
    assert user_result.login == login
    assert user_result.email == email
    assert user_result.role == role
    assert user_result.hashed_pwd
    assert token_result.user_agent == expected_user_agent


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, user_agent, expected_status, by_login",
    [
        (
                "test_login_name_1",
                "test_login_surname_1",
                "test_login_login_1",
                "test_login_email_1@mail.net",
                UserRole.user,
                "test_login_pwd_1",
                "test_login_user_agent_1",
                status.HTTP_200_OK,
                True,
        ),
        (
                "test_login_name_2",
                "test_login_surname_2",
                "test_login_login_2",
                "test_login_email_2@mail.net",
                UserRole.executor,
                "test_login_pwd_2",
                "test_login_user_agent_2",
                status.HTTP_200_OK,
                False,
        ),
    ],
)
async def test_login(client, name, surname, login, email, role, pwd, user_agent, expected_status, by_login):
    hashed_pwd = get_hashed_pwd(pwd)
    user_id = str(uuid4())
    values = {
        "id": user_id,
        "name": name,
        "surname": surname,
        "login": login,
        "email": email,
        "role": role,
        "hashed_pwd": hashed_pwd,
    }
    async with AsyncSession() as session:
        await session.execute(insert(User).values(**values))
        await session.commit()
    json = {
        "login_or_email": login if by_login else email,
        "pwd": pwd,
        "user_agent": user_agent,
    }

    response = client.post("/api/v1/users/login", json=json)
    response_json = response.json()
    async with AsyncSession() as session:
        token_result = await session.execute(select(Token).where(Token.subject == user_id))
        token_result = token_result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("access_token") is not None
    assert response_json.get("refresh_token") is not None
    assert len(response_json) == 2
    assert token_result is not None


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, user_agent, expected_status",
    [
        (
                "test_logout_name_1",
                "test_logout_surname_1",
                "test_logout_login_1",
                "test_logout_email_1@mail.net",
                UserRole.user,
                "test_logout_pwd_1",
                "Other / Other / Other",
                status.HTTP_204_NO_CONTENT,
        ),
        (
                "test_logout_name_2",
                "test_logout_surname_2",
                "test_logout_login_2",
                "test_logout_email_2@mail.net",
                UserRole.user,
                "test_logout_pwd_2",
                "Other / Other / Other",
                status.HTTP_204_NO_CONTENT,
        ),    ],
)
async def test_logout(client, user_data, name, surname, login, email, role, pwd, user_agent, expected_status):
    hashed_pwd = get_hashed_pwd(pwd)
    user_values = {
        "id": user_data.get("id"),
        "name": name,
        "surname": surname,
        "login": login,
        "email": email,
        "role": role,
        "hashed_pwd": hashed_pwd,
    }
    token_values = {"jti": str(uuid4()), "subject": user_data.get("id"), "user_agent": user_agent}
    async with AsyncSession() as session:
        await session.execute(insert(User).values(**user_values))
        await session.execute(insert(Token).values(**token_values))
        await session.commit()

    response = client.post(
        "/api/v1/users/logout",
        data={"user_agent": user_agent},
        cookies={"access_token": user_data.get("access_token")},
    )
    async with AsyncSession() as session:
        token_result = await session.execute(select(Token).where(Token.subject == user_data.get("id")))
        token_result = token_result.scalar()

    assert response.status_code == expected_status
    assert token_result is None













