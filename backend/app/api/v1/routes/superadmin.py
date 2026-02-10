"""
SuperAdmin management endpoints for tenant lifecycle and plan management.

All routes require superadmin role.

Tenant Management:
- POST /superadmin/tenants - Provision new tenant with config and admin user
- GET /superadmin/tenants - List tenants with config and usage
- GET /superadmin/tenants/{tenant_id} - Get tenant details with usage
- PUT /superadmin/tenants/{tenant_id} - Update tenant config (limits, features)
- POST /superadmin/tenants/{tenant_id}/suspend - Suspend tenant
- POST /superadmin/tenants/{tenant_id}/activate - Reactivate tenant
- PUT /superadmin/tenants/{tenant_id}/plan - Assign plan
- GET /superadmin/tenants/{tenant_id}/audit - Get audit log
- GET /superadmin/tenants/{tenant_id}/usage - Get usage stats

Plan Management:
- GET /superadmin/plans - List plans
- POST /superadmin/plans - Create plan
- PUT /superadmin/plans/{plan_id} - Update plan
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_superadmin
from app.models.tenant import Tenant
from app.models.tenant_audit_log import TenantAuditLog
from app.models.tenant_config import TenantConfig
from app.models.tenant_plan import TenantPlan
from app.models.user import User
from app.schemas.tenant_config import (
    AssignPlanRequest,
    SuspendTenantRequest,
    TenantAuditLogResponse,
    TenantConfigResponse,
    TenantConfigUpdate,
    TenantCreateWithConfig,
    TenantPlanCreate,
    TenantPlanResponse,
    TenantPlanUpdate,
    TenantUsageResponse,
    TenantWithConfigResponse,
)
from app.services.tenant_provisioning import tenant_provisioning_service
from app.services.tenant_status import tenant_status_service

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


# ---------------------------------------------------------------------------
# Tenant Management
# ---------------------------------------------------------------------------


@router.post(
    "/tenants",
    response_model=TenantWithConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
    data: TenantCreateWithConfig,
    request: Request,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Provision a new tenant with config, plan, and initial admin user."""
    # Validate unique slug
    result = await db.execute(
        select(Tenant).where(Tenant.slug == data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Validate unique admin email
    result = await db.execute(
        select(User).where(User.email == data.admin_email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email do admin ja existe",
        )

    try:
        provisioned = await tenant_provisioning_service.create_tenant_with_config(
            db,
            name=data.name,
            slug=data.slug,
            plan_id=data.plan_id,
            admin_email=data.admin_email,
            admin_password=data.admin_password,
            admin_full_name=data.admin_full_name,
            created_by_user_id=current_user.id,
            contract_type=data.contract_type,
            trial_days=data.trial_days,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    tenant = provisioned["tenant"]
    config = provisioned["config"]
    usage = await tenant_status_service.get_tenant_usage(db, tenant.id)

    return TenantWithConfigResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        config=_config_to_response(config),
        usage=TenantUsageResponse(**usage),
    )


@router.get("/tenants")
async def list_tenants(
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    plan_id: UUID | None = Query(None),
    search: str | None = Query(None),
):
    """List tenants with config and usage stats."""
    query = select(Tenant).outerjoin(
        TenantConfig, Tenant.id == TenantConfig.tenant_id
    )

    # Filters
    if status_filter:
        query = query.where(TenantConfig.status == status_filter)
    if plan_id:
        query = query.where(TenantConfig.plan_id == plan_id)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            Tenant.name.ilike(search_term) | Tenant.slug.ilike(search_term)
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * limit
    query = query.order_by(Tenant.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    tenants = result.scalars().all()

    # Build response with usage
    items = []
    for tenant in tenants:
        usage = await tenant_status_service.get_tenant_usage(db, tenant.id)
        items.append(
            TenantWithConfigResponse(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                is_active=tenant.is_active,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                config=_config_to_response(tenant.config) if tenant.config else None,
                usage=TenantUsageResponse(**usage),
            )
        )

    return {"items": [item.model_dump() for item in items], "total": total, "page": page}


@router.get("/tenants/{tenant_id}", response_model=TenantWithConfigResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Get tenant details with config and usage stats."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    usage = await tenant_status_service.get_tenant_usage(db, tenant.id)

    return TenantWithConfigResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        config=_config_to_response(tenant.config) if tenant.config else None,
        usage=TenantUsageResponse(**usage),
    )


@router.put("/tenants/{tenant_id}", response_model=TenantWithConfigResponse)
async def update_tenant_config(
    tenant_id: UUID,
    data: TenantConfigUpdate,
    request: Request,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Update tenant configuration (limits, features, contract_type)."""
    # Verify tenant exists
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    ip = request.client.host if request.client else None

    try:
        if data.limits_json is not None:
            await tenant_provisioning_service.update_tenant_limits(
                db,
                tenant_id=tenant_id,
                limits=data.limits_json,
                updated_by_user_id=current_user.id,
                ip_address=ip,
            )
        if data.features_json is not None:
            await tenant_provisioning_service.update_tenant_features(
                db,
                tenant_id=tenant_id,
                features=data.features_json,
                updated_by_user_id=current_user.id,
                ip_address=ip,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Update contract_type directly if provided
    if data.contract_type is not None:
        config_result = await db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = config_result.scalar_one_or_none()
        if config:
            config.contract_type = data.contract_type

    # Refresh and return
    await db.flush()
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    usage = await tenant_status_service.get_tenant_usage(db, tenant.id)

    return TenantWithConfigResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        config=_config_to_response(tenant.config) if tenant.config else None,
        usage=TenantUsageResponse(**usage),
    )


@router.post("/tenants/{tenant_id}/suspend", response_model=TenantConfigResponse)
async def suspend_tenant(
    tenant_id: UUID,
    data: SuspendTenantRequest,
    request: Request,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Suspend a tenant. Data is preserved but access is blocked."""
    try:
        config = await tenant_provisioning_service.suspend_tenant(
            db,
            tenant_id=tenant_id,
            reason=data.reason,
            suspended_by_user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return _config_to_response(config)


@router.post("/tenants/{tenant_id}/activate", response_model=TenantConfigResponse)
async def activate_tenant(
    tenant_id: UUID,
    request: Request,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Reactivate a suspended tenant."""
    try:
        config = await tenant_provisioning_service.activate_tenant(
            db,
            tenant_id=tenant_id,
            activated_by_user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return _config_to_response(config)


@router.put("/tenants/{tenant_id}/plan", response_model=TenantConfigResponse)
async def assign_plan(
    tenant_id: UUID,
    data: AssignPlanRequest,
    request: Request,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Assign a plan to a tenant. Copies plan limits/features to config."""
    try:
        config = await tenant_provisioning_service.assign_plan(
            db,
            tenant_id=tenant_id,
            plan_id=data.plan_id,
            assigned_by_user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return _config_to_response(config)


@router.get("/tenants/{tenant_id}/audit")
async def get_tenant_audit_log(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Get audit log entries for a tenant."""
    query = (
        select(TenantAuditLog)
        .where(TenantAuditLog.tenant_id == tenant_id)
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    offset = (page - 1) * limit
    query = query.order_by(TenantAuditLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    items = [
        TenantAuditLogResponse(
            id=log.id,
            tenant_id=log.tenant_id,
            admin_user_id=log.admin_user_id,
            action=log.action,
            old_values=log.old_values,
            new_values=log.new_values,
            reason=log.reason,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return {"items": [item.model_dump() for item in items], "total": total, "page": page}


@router.get("/tenants/{tenant_id}/usage", response_model=TenantUsageResponse)
async def get_tenant_usage(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Get resource usage stats for a tenant."""
    # Verify tenant exists
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    usage = await tenant_status_service.get_tenant_usage(db, tenant_id)
    return TenantUsageResponse(**usage)


# ---------------------------------------------------------------------------
# Plan Management
# ---------------------------------------------------------------------------


@router.get("/plans", response_model=list[TenantPlanResponse])
async def list_plans(
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """List all tenant plans."""
    result = await db.execute(
        select(TenantPlan).order_by(TenantPlan.created_at.asc())
    )
    plans = result.scalars().all()

    return [_plan_to_response(p) for p in plans]


@router.post(
    "/plans",
    response_model=TenantPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    data: TenantPlanCreate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant plan."""
    # Validate unique name
    result = await db.execute(
        select(TenantPlan).where(TenantPlan.name == data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de plano ja existe",
        )

    plan = TenantPlan(
        name=data.name,
        description=data.description,
        limits_json=data.limits.model_dump(),
        features_json=data.features.model_dump(),
        price_display=data.price_display,
        is_active=data.is_active,
    )
    db.add(plan)
    await db.flush()

    return _plan_to_response(plan)


@router.put("/plans/{plan_id}", response_model=TenantPlanResponse)
async def update_plan(
    plan_id: UUID,
    data: TenantPlanUpdate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Update a tenant plan."""
    result = await db.execute(
        select(TenantPlan).where(TenantPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano nao encontrado",
        )

    if data.name is not None:
        # Check uniqueness if name is changing
        if data.name != plan.name:
            dup_result = await db.execute(
                select(TenantPlan).where(TenantPlan.name == data.name)
            )
            if dup_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de plano ja existe",
                )
        plan.name = data.name
    if data.description is not None:
        plan.description = data.description
    if data.limits is not None:
        plan.limits_json = data.limits.model_dump()
    if data.features is not None:
        plan.features_json = data.features.model_dump()
    if data.price_display is not None:
        plan.price_display = data.price_display
    if data.is_active is not None:
        plan.is_active = data.is_active

    await db.flush()

    return _plan_to_response(plan)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _plan_to_response(plan: TenantPlan) -> TenantPlanResponse:
    """Convert TenantPlan model to response schema."""
    from app.schemas.tenant_config import TenantFeatures, TenantLimits

    return TenantPlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        limits=TenantLimits(**plan.limits_json) if plan.limits_json else TenantLimits(max_users=5, max_storage_gb=1, max_reports_month=50),
        features=TenantFeatures(**plan.features_json) if plan.features_json else TenantFeatures(),
        price_display=plan.price_display,
        is_active=plan.is_active,
        created_at=plan.created_at,
    )


def _config_to_response(config: TenantConfig) -> TenantConfigResponse:
    """Convert TenantConfig model to response schema."""
    plan_response = None
    if config.plan:
        plan_response = _plan_to_response(config.plan)

    return TenantConfigResponse(
        id=config.id,
        tenant_id=config.tenant_id,
        status=config.status,
        contract_type=config.contract_type,
        limits_json=config.limits_json,
        features_json=config.features_json,
        suspended_at=config.suspended_at,
        suspended_reason=config.suspended_reason,
        trial_ends_at=config.trial_ends_at,
        plan_id=config.plan_id,
        plan=plan_response,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )
