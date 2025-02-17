from uuid import uuid4

import pytest
from fastapi import status
from sqlalchemy import insert, select

from src.db.connector import AsyncSession
from src.db.tables import Token, User
from src.utils.auth import get_hashed_pwd
from src.utils.enums import UserRole
from tests.utils.tokens import create_refresh_token


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


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, user_agent, expected_status",
    [
        (
                "test_refresh_tokens_name_1",
                "test_refresh_tokens_surname_1",
                "test_refresh_tokens_login_1",
                "test_refresh_tokens_email_1@mail.net",
                UserRole.user,
                "test_refresh_tokens_pwd_1",
                "Other / Other / Other",
                status.HTTP_200_OK,
        ),
        (
                "test_refresh_tokens_name_2",
                "test_refresh_tokens_surname_2",
                "test_refresh_tokens_login_2",
                "test_refresh_tokens_email_2@mail.net",
                UserRole.executor,
                "test_refresh_tokens_pwd_2",
                "Other / Other / Other",
                status.HTTP_200_OK,
        ),    ],
)
async def test_refresh_tokens(client, name, surname, login, email, role, pwd, user_agent, expected_status):
    hashed_pwd = get_hashed_pwd(pwd)
    user_id = str(uuid4())
    user_values = {
        "id": user_id,
        "name": name,
        "surname": surname,
        "login": login,
        "email": email,
        "role": role,
        "hashed_pwd": hashed_pwd,
    }
    refresh_token_data = create_refresh_token(user_id, role)
    token_values = {"jti": refresh_token_data.get("jti"), "subject": user_id, "user_agent": user_agent}
    async with AsyncSession() as session:
        await session.execute(insert(User).values(**user_values))
        await session.execute(insert(Token).values(**token_values))
        await session.commit()

    response = client.post(
        "/api/v1/users/refresh",
        json={"refresh_token": refresh_token_data.get("refresh_token"), "user_agent": user_agent},
    )
    response_json = response.json()
    async with AsyncSession() as session:
        result = await session.execute(select(Token).where(Token.jti == refresh_token_data.get("jti")))
        result = result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("access_token") is not None
    assert response_json.get("refresh_token") is not None
    assert len(response_json) == 2
    assert result is None


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, expected_status",
    [
        (
                "test_get_user_data_name_1",
                "test_get_user_data_surname_1",
                "test_get_user_data_login_1",
                "test_get_user_data_email_1@mail.net",
                UserRole.user,
                "test_get_user_data_pwd_1",
                status.HTTP_200_OK,
        ),
        (
                "test_get_user_data_name_2",
                "test_get_user_data_surname_2",
                "test_get_user_data_login_2",
                "test_get_user_data_email_2@mail.net",
                UserRole.user,
                "test_get_user_data_pwd_2",
                status.HTTP_200_OK,
        ),    ],
)
async def test_get_user_data(client, user_data, name, surname, login, email, role, pwd, expected_status):
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
    async with AsyncSession() as session:
        await session.execute(insert(User).values(**user_values))
        await session.commit()

    response = client.get("/api/v1/users/me", cookies={"access_token": user_data.get("access_token")})
    response_json = response.json()

    assert response.status_code == expected_status
    assert response_json.get("name") == name
    assert response_json.get("surname") == surname
    assert response_json.get("login") == login
    assert response_json.get("email") == email
    assert response_json.get("role") == role


@pytest.mark.parametrize(
    "count, name, surname, login, email, role, pwd, expected_status, admin_prefix",
    [
        (
                2,
                "test_get_users_list_name_1",
                "test_get_users_list_sn_1",
                "test_get_users_list_login_1",
                "test_get_users_list_email_1@mail.net",
                UserRole.user,
                "test_get_users_list_pwd_1",
                status.HTTP_200_OK,
                "gSTwFVdsF",
        ),
        (
                5,
                "test_get_users_list_name_2",
                "test_get_users_list_sn_2",
                "test_get_users_list_login_2",
                "test_get_users_list_email_2@mail.net",
                UserRole.executor,
                "test_get_users_list_pwd_2",
                status.HTTP_200_OK,
                "VbshRqqs",
        ),    ],
)
async def test_get_users_list(
        client, admin_data, count, name, surname, login, email, role, pwd, expected_status, admin_prefix
):
    hashed_pwd = get_hashed_pwd(pwd)
    values = []
    for i in range(count):
        values.append({
            "id": str(uuid4()),
            "name": f"{name}_{i}",
            "surname": f"{surname}_{i}",
            "login": f"{login}_{i}",
            "email": f"{i}_{email}",
            "role": role,
            "hashed_pwd": hashed_pwd,
        })
    values.append({
        "id": admin_data.get("id"),
        "name": f"{admin_prefix}_name",
        "surname": f"{admin_prefix}_surname",
        "login": f"{admin_prefix}_login",
        "email": f"{admin_prefix}_email@mail.net",
        "role": UserRole.admin,
        "hashed_pwd": hashed_pwd,
    })
    async with AsyncSession() as session:
        await session.execute(insert(User).values(values))
        await session.commit()
    params = {"role": role}

    response = client.get(
        "/api/v1/users/list", params=params, cookies={"access_token": admin_data.get("access_token")}
    )
    response_json = response.json()

    assert response.status_code == expected_status
    assert ({item.get("id") for item in response_json} >=
            {item.get("id") for item in values if item.get("id") != admin_data.get("id")})
    assert ({item.get("name") for item in response_json} >=
            {item.get("name") for item in values if item.get("id") != admin_data.get("id")})
    assert ({item.get("surname") for item in response_json} >=
            {item.get("surname") for item in values if item.get("id") != admin_data.get("id")})
    assert ({item.get("login") for item in response_json} >=
            {item.get("login") for item in values if item.get("id") != admin_data.get("id")})
    assert ({item.get("email") for item in response_json} >=
            {item.get("email") for item in values if item.get("id") != admin_data.get("id")})
    assert {item.get("role") for item in response_json} == {role}


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, expected_status",
    [
        (
                "test_get_user_email_name_1",
                "test_get_user_email_surname_1",
                "test_get_user_email_login_1",
                "test_get_user_email_email_1@mail.net",
                UserRole.user,
                "test_get_user_email_pwd_1",
                status.HTTP_200_OK,
        ),
        (
                "test_get_user_email_name_2",
                "test_get_user_email_surname_2",
                "test_get_user_email_login_2",
                "test_get_user_email_email_2@mail.net",
                UserRole.user,
                "test_get_user_email_pwd_2",
                status.HTTP_200_OK,
        ),    ],
)
async def test_get_user_email(client, name, surname, login, email, role, pwd, expected_status):
    hashed_pwd = get_hashed_pwd(pwd)
    user_id = str(uuid4())
    user_values = {
        "id": user_id,
        "name": name,
        "surname": surname,
        "login": login,
        "email": email,
        "role": role,
        "hashed_pwd": hashed_pwd,
    }
    async with AsyncSession() as session:
        await session.execute(insert(User).values(**user_values))
        await session.commit()

    response = client.get(f"/api/v1/users/{user_id}/email")
    response_json = response.json()

    assert response.status_code == expected_status
    assert response_json == email


@pytest.mark.parametrize(
    "name, surname, login, email, role, pwd, expected_status, admin_prefix",
    [
        (
                "test_delete_name_1",
                "test_delete_surname_1",
                "test_delete_login_1",
                "test_delete_email_1@mail.net",
                UserRole.user,
                "test_delete_pwd_1",
                status.HTTP_204_NO_CONTENT,
                "MsfjKfgcsafH",
        ),
        (
                "test_delete_name_2",
                "test_delete_surname_2",
                "test_delete_login_2",
                "test_delete_email_2@mail.net",
                UserRole.executor,
                "test_delete_pwd_2",
                status.HTTP_204_NO_CONTENT,
                "zcTasffYYWwe",
        ),    ],
)
async def test_delete(client, admin_data, name, surname, login, email, role, pwd, expected_status, admin_prefix):
    hashed_pwd = get_hashed_pwd(pwd)
    user_id = str(uuid4())
    values = [
        {
            "id": user_id,
            "name": name,
            "surname": surname,
            "login": login,
            "email": email,
            "role": role,
            "hashed_pwd": hashed_pwd,
        },
        {
            "id": admin_data.get("id"),
            "name": f"{admin_prefix}_name",
            "surname": f"{admin_prefix}_surname",
            "login": f"{admin_prefix}_login",
            "email": f"{admin_prefix}_email@mail.net",
            "role": UserRole.admin,
            "hashed_pwd": hashed_pwd,
        },
    ]
    async with AsyncSession() as session:
        await session.execute(insert(User).values(values))
        await session.commit()

    response = client.delete(f"/api/v1/users/{user_id}", cookies={"access_token": admin_data.get("access_token")})
    async with AsyncSession() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        result = result.scalar()

    assert response.status_code == expected_status
    assert result is None
