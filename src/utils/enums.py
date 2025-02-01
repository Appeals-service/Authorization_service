from enum import StrEnum


class UserRole(StrEnum):
    admin = "admin"
    user = "user"
    executor = "executor"


class TokenType(StrEnum):
    access = "acc"
    refresh = "ref"
