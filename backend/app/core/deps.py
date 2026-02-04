"""
FastAPI dependencies for authentication and authorization.

This module provides:
- oauth2_scheme: OAuth2 bearer token extraction
- get_current_user: Dependency to get authenticated user from JWT
- require_role: Dependency factory for role-based access control
- require_superadmin: Dependency for superadmin-only routes
- require_tenant_admin: Dependency for tenant admin and above
- get_tenant_filter: Dependency for tenant-scoped queries
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.user import UserRole, ROLE_HIERARCHY


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
            user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))]
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


def require_minimum_role(min_role: UserRole):
    """
    Dependency that requires at least a minimum role level.

    Usage:
        @router.get("/managers-and-above")
        async def route(
            user: Annotated[User, Depends(require_minimum_role(UserRole.PROJECT_MANAGER))]
        ):
            ...

    Args:
        min_role: Minimum role required

    Returns:
        Dependency function that validates user role level
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cargo invalido: {current_user.role}"
            )

        user_level = ROLE_HIERARCHY.get(user_role, 0)
        min_level = ROLE_HIERARCHY.get(min_role, 100)

        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado - requer no minimo {min_role.value}"
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


async def require_tenant_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user is at least tenant_admin level.
    superadmin also passes this check.

    Usage:
        @router.post("/users")
        async def create_user(
            user: Annotated[User, Depends(require_tenant_admin)],
            user_data: UserCreate
        ):
            ...

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User object if role is superadmin or tenant_admin

    Raises:
        HTTPException 403: If user role is not superadmin or tenant_admin
    """
    allowed = {"superadmin", "tenant_admin"}
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - requer tenant_admin ou superior"
        )
    return current_user


async def require_project_manager(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user is at least project_manager level.
    superadmin and tenant_admin also pass this check.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User object if role is superadmin, tenant_admin, or project_manager

    Raises:
        HTTPException 403: If user role is below project_manager level
    """
    allowed = {"superadmin", "tenant_admin", "project_manager"}
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - requer project_manager ou superior"
        )
    return current_user


async def get_tenant_filter(
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id_param: UUID | None = Query(None, alias="tenant_id"),
) -> UUID | None:
    """
    Dependency to get tenant_id for query filtering.

    Behavior:
    - superadmin: Can specify any tenant_id via query param, or None for all tenants
    - Others: Always returns their own tenant_id (ignores query param)

    Usage:
        @router.get("/reports")
        async def list_reports(
            tenant_id: Annotated[UUID | None, Depends(get_tenant_filter)],
            db: AsyncSession = Depends(get_db)
        ):
            if tenant_id:
                result = await db.execute(
                    select(Report).where(Report.tenant_id == tenant_id)
                )
            else:
                # Only superadmin reaches here - query all tenants
                result = await db.execute(select(Report))
            return result.scalars().all()

    Args:
        current_user: Authenticated user from get_current_user
        tenant_id_param: Optional tenant_id from query string

    Returns:
        UUID of tenant for filtering, or None for superadmin cross-tenant queries
    """
    if current_user.role == "superadmin":
        return tenant_id_param  # Can be None for cross-tenant queries

    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inconsistencia: usuario nao-superadmin sem tenant_id"
        )

    return current_user.tenant_id


async def require_same_tenant_or_superadmin(
    current_user: Annotated[User, Depends(get_current_user)],
    target_tenant_id: UUID,
) -> bool:
    """
    Verify user can access a specific tenant's data.

    - superadmin: Can access any tenant
    - Others: Can only access their own tenant

    Args:
        current_user: Authenticated user
        target_tenant_id: The tenant ID being accessed

    Returns:
        True if access is allowed

    Raises:
        HTTPException 403: If access is denied
    """
    if current_user.role == "superadmin":
        return True

    if current_user.tenant_id != target_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este tenant"
        )
    return True
