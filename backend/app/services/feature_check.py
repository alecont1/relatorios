"""
Feature flag checking utility.

Resolves feature flags through the chain:
1. TenantConfig.features_json (per-tenant override)
2. TenantPlan.features_json (plan default)
3. Default: False
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tenant_config import TenantConfig


async def check_feature(db: AsyncSession, tenant_id: UUID, feature: str) -> bool:
    """
    Check if a feature is enabled for a tenant.

    Resolution order:
    1. TenantConfig.features_json override
    2. TenantPlan.features_json default
    3. False

    Args:
        db: Database session
        tenant_id: Tenant UUID
        feature: Feature name (e.g., "custom_pdf")

    Returns:
        True if feature is enabled
    """
    result = await db.execute(
        select(TenantConfig)
        .options(selectinload(TenantConfig.plan))
        .where(TenantConfig.tenant_id == tenant_id)
    )
    config = result.scalar_one_or_none()

    if config is None:
        return False

    # 1. Check tenant-level override
    if config.features_json and feature in config.features_json:
        return bool(config.features_json[feature])

    # 2. Check plan-level default
    if config.plan and config.plan.features_json and feature in config.plan.features_json:
        return bool(config.plan.features_json[feature])

    # 3. Default
    return False
