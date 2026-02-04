"""
User CRUD endpoints for admin user management.

This module provides:
- POST /users/ - Create user (tenant_admin/superadmin only)
- GET /users/ - List users with pagination
- GET /users/{user_id} - Get specific user
- PATCH /users/{user_id} - Update user
- DELETE /users/{user_id} - Hard delete user

RBAC:
- tenant_admin: Can only manage users in their own tenant
- superadmin: Can manage users in any tenant
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_tenant_admin, get_current_user
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    UserRole,
    TENANT_BOUND_ROLES,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.

    - tenant_admin: Can only create users in their own tenant
    - superadmin: Can create users in any tenant

    Role restrictions:
    - tenant_admin cannot create superadmin users
    - tenant_admin can only create: tenant_admin, project_manager, technician, viewer
    """
    # Determine tenant_id
    if current_user.role == "superadmin":
        # Superadmin can specify tenant, or None for creating another superadmin
        if user_data.role == UserRole.SUPERADMIN:
            tenant_id = None  # Superadmin has no tenant
        else:
            tenant_id = user_data.tenant_id
            if tenant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"tenant_id é obrigatório para o cargo '{user_data.role.value}'",
                )
    else:
        # tenant_admin can only create in their tenant
        tenant_id = current_user.tenant_id
        if user_data.tenant_id and user_data.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admin só pode criar usuários no próprio tenant",
            )

    # tenant_admin cannot create superadmin or other tenant_admins
    if current_user.role == "tenant_admin":
        if user_data.role == UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admin não pode criar usuários superadmin",
            )
        # tenant_admin CAN create other tenant_admins in their tenant
        # This allows delegation within the organization

    # Validate role can be managed by current user
    if not current_user.can_manage_role(user_data.role.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Você não tem permissão para criar usuários com o cargo '{user_data.role.value}'",
        )

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        )

    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=user_data.role.value,
        tenant_id=tenant_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    List users.

    - tenant_admin: Sees only users in their tenant
    - superadmin: Sees all users
    """
    # Build query
    query = select(User)

    if current_user.role != "superadmin":
        # tenant_admin sees only their tenant
        query = query.where(User.tenant_id == current_user.tenant_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total or 0,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # tenant_admin can only see users in their tenant
    if current_user.role != "superadmin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Update a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # tenant_admin can only update users in their tenant
    if current_user.role != "superadmin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    # Validate role change permissions
    if user_data.role is not None:
        # tenant_admin cannot promote to superadmin
        if current_user.role == "tenant_admin" and user_data.role == UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admin não pode promover usuários a superadmin",
            )

        # Check if user can manage the target role
        if not current_user.can_manage_role(user_data.role.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você não tem permissão para definir o cargo '{user_data.role.value}'",
            )

    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role is not None:
        user.role = user_data.role.value
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user.

    Per CONTEXT.md: hard delete only (no soft delete).
    Note: Check for dependent reports before deleting.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # tenant_admin can only delete users in their tenant
    if current_user.role != "superadmin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    # Cannot delete yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir o próprio usuário",
        )

    # Cannot delete superadmin unless you are superadmin
    if user.role == "superadmin" and current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas superadmin pode excluir outro superadmin",
        )

    # TODO: In Phase 6, check for reports and reassign or block
    # For now, just delete (no reports exist yet)

    await db.delete(user)
    await db.commit()

    return None
