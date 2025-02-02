"""User schemas."""

from pydantic import BaseModel, Field, EmailStr, field_validator

from utils.enums import UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=3, max_length=30, examples=["John"])
    surname: str = Field(min_length=3, max_length=30, examples=["Doe"])
    login: str = Field(min_length=3, max_length=30, examples=["Sunny_Johnny"])
    email: EmailStr = Field(min_length=7, max_length=50, examples=["john_doe@mail.net"])
    role: UserRole = Field(default=UserRole.user, examples=[UserRole.user])

    class Config:
        str_strip_whitespace = True

    @field_validator("email")
    @classmethod
    def email_normalize(cls, value: str) -> str:
        return value.lower()


class UserCreate(UserBase):
    pwd: str = Field(min_length=5, max_length=50, serialization_alias="hashed_pwd")
    user_agent: str


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class UserAuth(BaseModel):
    login_or_email: str = Field(min_length=3, max_length=50, examples=["john_doe@mail.net"])
    pwd: str = Field(min_length=5, max_length=50)
