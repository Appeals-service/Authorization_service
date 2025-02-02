"""Role checker module"""

from fastapi import Depends, HTTPException, status

from db.tables import User
from utils.auth import get_current_user
from utils.enums import UserRole


class RoleChecker:

    def __init__(self, allowed_roles: set[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:

        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
        return user


allowed_for_admin = RoleChecker({UserRole.admin})
allowed_for_all = RoleChecker({role for role in UserRole})
