
from fastapi import Depends, HTTPException, status

from backend.app.core.dependencies import get_current_user
from backend.app.models.user import Role, User


def require_roles(*allowed_roles: Role):
    """Allow the request only if the logged-in user has one of these roles."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return checker