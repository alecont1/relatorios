#!/usr/bin/env python3
"""
Script to create initial admin user for SmartHand.

Usage:
    cd backend
    python scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Windows event loop fix for psycopg
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import engine, async_session
from app.core.security import hash_password
# Import all models to ensure SQLAlchemy relationships are resolved
import app.models  # noqa: F401
from app.models import Tenant, User


async def create_admin():
    """Create a default tenant and admin user."""

    async with async_session() as db:
        # Check if tenant exists
        result = await db.execute(select(Tenant).where(Tenant.slug == "demo"))
        tenant = result.scalar_one_or_none()

        if not tenant:
            print("Creating demo tenant...")
            tenant = Tenant(
                name="Demo Company",
                slug="demo",
                is_active=True,
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
            print(f"  Tenant created: {tenant.name} (ID: {tenant.id})")
        else:
            print(f"Tenant already exists: {tenant.name}")

        # Check if admin user exists
        result = await db.execute(
            select(User).where(User.email == "admin@smarthand.com")
        )
        user = result.scalar_one_or_none()

        if not user:
            print("Creating admin user...")
            user = User(
                tenant_id=tenant.id,
                email="admin@smarthand.com",
                password_hash=hash_password("admin123"),
                full_name="Administrador",
                role="superadmin",
                is_active=True,
            )
            db.add(user)
            await db.commit()
            print(f"  User created: {user.email}")
        else:
            print(f"User already exists: {user.email}")

        print("\n" + "="*50)
        print("Login credentials:")
        print("  Email: admin@smarthand.com")
        print("  Password: admin123")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(create_admin())
