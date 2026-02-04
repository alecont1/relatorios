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
from app.models import Tenant, User, Project
import uuid


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

        # Check if superadmin user exists (global admin without tenant)
        result = await db.execute(
            select(User).where(User.email == "admin@smarthand.com.br")
        )
        superadmin = result.scalar_one_or_none()

        if not superadmin:
            print("Creating superadmin user...")
            superadmin = User(
                tenant_id=None,  # Superadmin has NO tenant
                email="admin@smarthand.com.br",
                password_hash=hash_password("admin123"),
                full_name="Administrador SmartHand",
                role="superadmin",
                is_active=True,
            )
            db.add(superadmin)
            await db.commit()
            print(f"  Superadmin created: {superadmin.email}")
        else:
            print(f"Superadmin already exists: {superadmin.email}")

        # Check if demo tenant admin exists
        result = await db.execute(
            select(User).where(User.email == "admin@demo.com")
        )
        tenant_admin = result.scalar_one_or_none()

        if not tenant_admin:
            print("Creating tenant admin user...")
            tenant_admin = User(
                tenant_id=tenant.id,  # Tenant admin MUST have tenant
                email="admin@demo.com",
                password_hash=hash_password("admin123"),
                full_name="Administrador Demo",
                role="tenant_admin",
                is_active=True,
            )
            db.add(tenant_admin)
            await db.commit()
            print(f"  Tenant admin created: {tenant_admin.email}")
        else:
            print(f"Tenant admin already exists: {tenant_admin.email}")

        # Check if default project exists (using the placeholder UUID from frontend)
        default_project_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        result = await db.execute(
            select(Project).where(Project.id == default_project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            print("Creating default project...")
            project = Project(
                id=default_project_id,
                tenant_id=tenant.id,
                name="Projeto Padrao",
                description="Projeto padrao para relatorios sem projeto especifico",
                client_name="Cliente Geral",
                is_active=True,
            )
            db.add(project)
            await db.commit()
            print(f"  Project created: {project.name} (ID: {project.id})")
        else:
            print(f"Default project already exists: {project.name}")

        print("\n" + "="*50)
        print("Login credentials:")
        print("  Superadmin: admin@smarthand.com.br / admin123")
        print("  Tenant Admin (Demo): admin@demo.com / admin123")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(create_admin())
