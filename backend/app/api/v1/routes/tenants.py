"""
Tenant CRUD endpoints for superadmin.

This module provides:
- POST /tenants/ - Create tenant (superadmin only)
- GET /tenants/ - List all tenants with pagination
- GET /tenants/{tenant_id} - Get specific tenant
- PATCH /tenants/{tenant_id} - Update tenant (name, is_active only)

Note: Slug is immutable after creation to avoid R2 object key migrations.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_superadmin
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
)

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new tenant organization.

    Slug must be unique and will be immutable after creation.
    All new tenants are created as active (is_active=True).
    """
    # Check slug uniqueness
    result = await db.execute(
        select(Tenant).where(Tenant.slug == tenant_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    tenant = Tenant(
        name=tenant_data.name,
        slug=tenant_data.slug,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    return TenantResponse.model_validate(tenant)


@router.get("", response_model=TenantListResponse)
async def list_tenants(
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_inactive: bool = Query(False),
):
    """
    List all tenant organizations.

    By default shows only active tenants.
    Use include_inactive=true to see all tenants.
    """
    query = select(Tenant)

    if not include_inactive:
        query = query.where(Tenant.is_active == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Tenant.created_at.desc())
    result = await db.execute(query)
    tenants = result.scalars().all()

    return TenantListResponse(
        tenants=[TenantResponse.model_validate(t) for t in tenants],
        total=total or 0,
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tenant by ID."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    return TenantResponse.model_validate(tenant)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update a tenant organization.

    Only name and is_active can be updated.
    Slug is immutable to preserve R2 object key consistency.
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    # Update allowed fields only
    if tenant_data.name is not None:
        tenant.name = tenant_data.name
    if tenant_data.is_active is not None:
        tenant.is_active = tenant_data.is_active

    await db.commit()
    await db.refresh(tenant)

    return TenantResponse.model_validate(tenant)
