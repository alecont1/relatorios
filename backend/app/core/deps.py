"""
FastAPI dependencies for authentication and authorization.

This module provides:
- oauth2_scheme: OAuth2 bearer token extraction
- get_current_user: Dependency to get authenticated user from JWT
- require_role: Dependency factory for role-based access control
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User


# OAuth2 scheme for extracting bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inativo"
        )

    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control.

    Usage:
        @router.get("/admin-only")
        async def admin_route(
            user: Annotated[User, Depends(require_role("admin", "superadmin"))]
        ):
            ...

    Args:
        *allowed_roles: Roles that are allowed to access the route

    Returns:
        Dependency function that validates user role
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado - permissao insuficiente"
            )
        return current_user
    return role_checker


async def require_superadmin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure only superadmin users can access a route.

    Usage:
        @router.post("/tenants")
        async def create_tenant(
            user: Annotated[User, Depends(require_superadmin)],
            tenant_data: TenantCreate
        ):
            ...

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User object if role is superadmin

    Raises:
        HTTPException 403: If user role is not superadmin
    """
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - apenas superadmin"
        )
    return current_user


async def get_tenant_filter(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UUID:
    """
    Dependency to get current user's tenant_id for query filtering.

    This ensures tenant data isolation in multi-tenant queries.

    Usage:
        @router.get("/reports")
        async def list_reports(
            tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
            db: AsyncSession = Depends(get_db)
        ):
            result = await db.execute(
                select(Report).where(Report.tenant_id == tenant_id)
            )
            return result.scalars().all()

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        UUID of user's tenant for filtering queries
    """
    return current_user.tenant_id
