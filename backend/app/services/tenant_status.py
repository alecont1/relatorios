"""
Tenant status service - handles tenant status checks and limit enforcement.

Provides utilities for checking tenant operational status, calculating
resource usage, and enforcing plan limits.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.models.report_photo import ReportPhoto
from app.models.tenant_config import TenantConfig
from app.models.user import User


class TenantStatusService:
    """Handles tenant status checks and enforcement."""

    async def check_tenant_status(
        self, db: AsyncSession, tenant_id: uuid.UUID
    ) -> TenantConfig:
        """
        Get current tenant config. Raises HTTP 423 if suspended.

        Returns the TenantConfig if tenant is operational.
        """
        result = await db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = result.scalar_one_or_none()
        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuracao nao encontrada para tenant {tenant_id}",
            )

        if config.status == "suspended":
            raise HTTPException(
                status_code=423,
                detail=f"Tenant suspenso: {config.suspended_reason or 'Sem motivo informado'}",
            )

        return config

    async def get_tenant_usage(
        self, db: AsyncSession, tenant_id: uuid.UUID
    ) -> dict:
        """
        Calculate current resource usage for a tenant.

        Returns:
            dict with users_count, storage_used_gb, reports_this_month
        """
        # Count active users
        users_result = await db.execute(
            select(func.count(User.id)).where(
                User.tenant_id == tenant_id,
                User.is_active == True,
            )
        )
        users_count = users_result.scalar() or 0

        # Approximate storage used (sum of photo file sizes)
        storage_result = await db.execute(
            select(func.coalesce(func.sum(ReportPhoto.file_size_bytes), 0)).where(
                ReportPhoto.report_id.in_(
                    select(Report.id).where(Report.tenant_id == tenant_id)
                )
            )
        )
        storage_bytes = storage_result.scalar() or 0
        storage_gb = round(storage_bytes / (1024 ** 3), 2)

        # Reports created this month
        now = datetime.now(timezone.utc)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        reports_result = await db.execute(
            select(func.count(Report.id)).where(
                Report.tenant_id == tenant_id,
                Report.created_at >= first_of_month,
            )
        )
        reports_this_month = reports_result.scalar() or 0

        return {
            "users_count": users_count,
            "storage_used_gb": storage_gb,
            "reports_this_month": reports_this_month,
        }

    async def check_limits(
        self, db: AsyncSession, tenant_id: uuid.UUID, action: str
    ) -> bool:
        """
        Check if tenant can perform an action within limits.

        Args:
            action: 'create_user' | 'create_report' | 'upload_photo'

        Returns True if within limits.
        Raises HTTP 429 if limit exceeded.
        """
        result = await db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = result.scalar_one_or_none()
        if config is None:
            return True  # No config = no limits enforced

        limits = config.limits_json or {}
        usage = await self.get_tenant_usage(db, tenant_id)

        if action == "create_user":
            max_users = limits.get("max_users")
            if max_users is not None and usage["users_count"] >= max_users:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de usuarios atingido ({max_users})",
                )

        elif action == "create_report":
            max_reports = limits.get("max_reports_month")
            if max_reports is not None and usage["reports_this_month"] >= max_reports:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de relatorios mensais atingido ({max_reports})",
                )

        elif action == "upload_photo":
            max_storage = limits.get("max_storage_gb")
            if max_storage is not None and usage["storage_used_gb"] >= max_storage:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de armazenamento atingido ({max_storage} GB)",
                )

        return True

    async def get_expiring_trials(
        self, db: AsyncSession, days_ahead: int = 7
    ) -> list[TenantConfig]:
        """
        Find tenants with trials expiring within N days.

        Returns list of TenantConfig objects for tenants in trial
        status whose trial_ends_at is within the specified window.
        """
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)

        result = await db.execute(
            select(TenantConfig).where(
                TenantConfig.status == "trial",
                TenantConfig.trial_ends_at.isnot(None),
                TenantConfig.trial_ends_at <= cutoff,
                TenantConfig.trial_ends_at >= now,
            )
        )
        return list(result.scalars().all())


# Singleton instance
tenant_status_service = TenantStatusService()
