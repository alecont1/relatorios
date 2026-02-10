#!/usr/bin/env python3
"""
Seed default tenant plans for the SmartHand system.

Creates three standard plans: Free, Pro, and Enterprise.

Usage:
    python scripts/seed_plans.py
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows event loop compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.tenant_plan import TenantPlan

engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

PLANS = [
    {
        "name": "Free",
        "description": "Plano gratuito para testes e pequenas equipes",
        "limits_json": {
            "max_users": 5,
            "max_storage_gb": 1,
            "max_reports_month": 50,
        },
        "features_json": {
            "gps_required": True,
            "certificate_required": False,
            "export_excel": False,
            "watermark": True,
            "custom_pdf": False,
        },
        "price_display": "Gratuito",
        "is_active": True,
    },
    {
        "name": "Pro",
        "description": "Plano profissional para equipes em crescimento",
        "limits_json": {
            "max_users": 25,
            "max_storage_gb": 10,
            "max_reports_month": 500,
        },
        "features_json": {
            "gps_required": True,
            "certificate_required": True,
            "export_excel": True,
            "watermark": True,
            "custom_pdf": False,
        },
        "price_display": "R$ 199/mes",
        "is_active": True,
    },
    {
        "name": "Enterprise",
        "description": "Plano empresarial com recursos ilimitados",
        "limits_json": {
            "max_users": 999,
            "max_storage_gb": 100,
            "max_reports_month": 9999,
        },
        "features_json": {
            "gps_required": True,
            "certificate_required": True,
            "export_excel": True,
            "watermark": True,
            "custom_pdf": True,
        },
        "price_display": "Sob consulta",
        "is_active": True,
    },
]


async def main() -> None:
    """Seed default plans (skip existing by name)."""
    print("=" * 50)
    print("  SmartHand - Seed Plans")
    print("=" * 50)

    async with SessionLocal() as session:
        created = 0
        skipped = 0

        for plan_data in PLANS:
            # Check if plan with this name already exists
            result = await session.execute(
                select(TenantPlan).where(TenantPlan.name == plan_data["name"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  SKIP: '{plan_data['name']}' already exists (id={existing.id})")
                skipped += 1
                continue

            plan = TenantPlan(
                id=uuid.uuid4(),
                name=plan_data["name"],
                description=plan_data["description"],
                limits_json=plan_data["limits_json"],
                features_json=plan_data["features_json"],
                price_display=plan_data["price_display"],
                is_active=plan_data["is_active"],
            )
            session.add(plan)
            created += 1
            print(f"  CREATE: '{plan_data['name']}' - {plan_data['price_display']}")

        await session.commit()

        print(f"\n  Created: {created}, Skipped: {skipped}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
