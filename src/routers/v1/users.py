from fastapi import APIRouter, Depends, status, Body

from db.tables import User
from dto.schemas.users import UserCreate, UserAuth, UserBase, Tokens
from services.user import UserService
from utils.role_checker import allowed_for_all

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/registration",
    response_model=Tokens,
    summary="User registration",
    response_description="Tokens",
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate):
    return await UserService.register(user_data)


@router.post(
    "/login",
    response_model=Tokens,
    summary="User login",
    response_description="Tokens",
)
async def login(user_data: UserAuth):
    return await UserService.login(user_data)


@router.post(
    "/logout",
    summary="User logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(user_agent: str = Body(), user: User = Depends(allowed_for_all)):
    await UserService.logout(user, user_agent)


@router.post(
    "/refresh",
    response_model=Tokens,
    summary="Refresh tokens",
    response_description="Tokens",
)
async def refresh_tokens(refresh_token: str = Body(), user_agent: str = Body()):
    return await UserService.refresh(refresh_token, user_agent)


@router.get(
    "/me",
    response_model=UserBase,
    summary="Get current user data",
    response_description="User data",
)
async def get_user_data(user: User = Depends(allowed_for_all)):
    return user
