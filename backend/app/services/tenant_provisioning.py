"""
Tenant provisioning service - handles tenant lifecycle management.

Provides transactional operations for creating, suspending, activating,
and configuring tenants with full audit logging.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.tenant_audit_log import TenantAuditLog
from app.models.tenant_config import TenantConfig
from app.models.tenant_plan import TenantPlan
from app.models.tenant_onboarding import TenantOnboarding
from app.models.user import User


class TenantProvisioningService:
    """Handles tenant lifecycle: creation, configuration, suspension."""

    async def create_tenant_with_config(
        self,
        db: AsyncSession,
        *,
        name: str,
        slug: str,
        plan_id: uuid.UUID,
        admin_email: str,
        admin_password: str,
        admin_full_name: str,
        created_by_user_id: uuid.UUID,
        contract_type: str | None = None,
        trial_days: int = 14,
        ip_address: str | None = None,
    ) -> dict:
        """
        Full tenant provisioning in a single transaction.

        1. Validate plan exists and is active
        2. Create Tenant record
        3. Create TenantConfig linked to plan with copied limits/features
        4. Create admin User (role=tenant_admin)
        5. Log audit entry (action=tenant_created)

        Returns dict with tenant, config, and admin_user.
        """
        # 1. Load and validate plan
        result = await db.execute(
            select(TenantPlan).where(TenantPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")
        if not plan.is_active:
            raise ValueError(f"Plan '{plan.name}' is not active")

        # 2. Create tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            is_active=True,
        )
        db.add(tenant)
        await db.flush()

        # 3. Create tenant config
        trial_ends = datetime.now(timezone.utc) + timedelta(days=trial_days) if trial_days > 0 else None
        config = TenantConfig(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            plan_id=plan.id,
            status="trial" if trial_days > 0 else "active",
            contract_type=contract_type,
            limits_json=plan.limits_json,
            features_json=plan.features_json,
            trial_ends_at=trial_ends,
        )
        db.add(config)

        # 4. Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email=admin_email,
            password_hash=hash_password(admin_password),
            full_name=admin_full_name,
            role="tenant_admin",
            is_active=True,
        )
        db.add(admin_user)

        # 5. Create onboarding record
        onboarding = TenantOnboarding(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
        )
        db.add(onboarding)

        # 6. Audit log
        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            admin_user_id=created_by_user_id,
            action="tenant_created",
            new_values={
                "name": name,
                "slug": slug,
                "plan": plan.name,
                "admin_email": admin_email,
                "trial_days": trial_days,
            },
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return {
            "tenant": tenant,
            "config": config,
            "admin_user": admin_user,
        }

    async def suspend_tenant(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        reason: str,
        suspended_by_user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> TenantConfig:
        """
        Suspend a tenant. Does NOT delete any data.

        Sets config.status='suspended', records timestamp and reason,
        and logs an audit entry.
        """
        config = await self._get_config_or_raise(db, tenant_id)
        old_status = config.status

        now = datetime.now(timezone.utc)
        config.status = "suspended"
        config.suspended_at = now
        config.suspended_reason = reason

        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            admin_user_id=suspended_by_user_id,
            action="tenant_suspended",
            old_values={"status": old_status},
            new_values={"status": "suspended", "reason": reason},
            reason=reason,
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return config

    async def activate_tenant(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        activated_by_user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> TenantConfig:
        """
        Reactivate a suspended tenant.

        Sets config.status='active', clears suspension fields,
        and logs an audit entry.
        """
        config = await self._get_config_or_raise(db, tenant_id)
        old_status = config.status

        config.status = "active"
        config.suspended_at = None
        config.suspended_reason = None

        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            admin_user_id=activated_by_user_id,
            action="tenant_activated",
            old_values={"status": old_status},
            new_values={"status": "active"},
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return config

    async def update_tenant_limits(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        limits: dict,
        updated_by_user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> TenantConfig:
        """Update limits_json and log audit with old/new values."""
        config = await self._get_config_or_raise(db, tenant_id)
        old_limits = config.limits_json

        config.limits_json = limits

        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            admin_user_id=updated_by_user_id,
            action="limits_updated",
            old_values={"limits": old_limits},
            new_values={"limits": limits},
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return config

    async def update_tenant_features(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        features: dict,
        updated_by_user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> TenantConfig:
        """Update features_json and log audit with old/new values."""
        config = await self._get_config_or_raise(db, tenant_id)
        old_features = config.features_json

        config.features_json = features

        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            admin_user_id=updated_by_user_id,
            action="features_updated",
            old_values={"features": old_features},
            new_values={"features": features},
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return config

    async def assign_plan(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        plan_id: uuid.UUID,
        assigned_by_user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> TenantConfig:
        """
        Assign a plan to a tenant.

        Loads plan defaults, updates config.plan_id and copies
        plan limits/features to the config. Logs an audit entry.
        """
        # Validate plan
        result = await db.execute(
            select(TenantPlan).where(TenantPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")
        if not plan.is_active:
            raise ValueError(f"Plan '{plan.name}' is not active")

        config = await self._get_config_or_raise(db, tenant_id)
        old_plan_id = str(config.plan_id) if config.plan_id else None

        config.plan_id = plan.id
        config.limits_json = plan.limits_json
        config.features_json = plan.features_json

        audit = TenantAuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            admin_user_id=assigned_by_user_id,
            action="plan_changed",
            old_values={"plan_id": old_plan_id},
            new_values={"plan_id": str(plan.id), "plan_name": plan.name},
            ip_address=ip_address,
        )
        db.add(audit)
        await db.flush()

        return config

    async def _get_config_or_raise(
        self, db: AsyncSession, tenant_id: uuid.UUID
    ) -> TenantConfig:
        """Load TenantConfig by tenant_id or raise ValueError."""
        result = await db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = result.scalar_one_or_none()
        if config is None:
            raise ValueError(f"Configuration not found for tenant {tenant_id}")
        return config


# Singleton instance
tenant_provisioning_service = TenantProvisioningService()
