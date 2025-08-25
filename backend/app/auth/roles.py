from enum import Enum
from typing import List

from fastapi import Depends, HTTPException, status

from ..api.deps import get_current_user
from ..models.user import User


class Role(str, Enum):
    """Available user roles."""

    admin = "admin"
    org_member = "org_member"
    project_contributor = "project_contributor"


def require_roles(required_roles: List[Role]):
    """FastAPI dependency enforcing that the current user has one of the required roles."""

    def role_dependency(user: User = Depends(get_current_user)):
        user_roles = set(getattr(user, "roles", []))
        if not user_roles.intersection({r.value for r in required_roles}):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return role_dependency
