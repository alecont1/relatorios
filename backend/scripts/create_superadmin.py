#!/usr/bin/env python3
"""
Create a superadmin user in the system.

Usage:
    python scripts/create_superadmin.py

This script will create a superadmin user with:
- tenant_id = NULL (global access)
- role = "superadmin"
- is_active = True

You will be prompted for email, full name, and password.
"""

import asyncio
import sys
from getpass import getpass

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from sqlalchemy import select
from app.core.database import async_engine, AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def create_superadmin():
    """Create a superadmin user interactively."""
    print("\n=== Create Superadmin User ===\n")

    # Get user input
    email = input("Email: ").strip()
    if not email:
        print("Error: Email is required")
        return

    full_name = input("Full name: ").strip()
    if not full_name:
        print("Error: Full name is required")
        return

    password = getpass("Password: ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        return

    # Connect to database
    async with AsyncSessionLocal() as db:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"\nError: User with email '{email}' already exists")
            return

        # Check if there's already a superadmin
        result = await db.execute(select(User).where(User.role == "superadmin"))
        existing_superadmin = result.scalar_one_or_none()

        if existing_superadmin:
            print(f"\nWarning: A superadmin already exists: {existing_superadmin.email}")
            confirm = input("Create another superadmin? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Aborted")
                return

        # Create superadmin
        superadmin = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role="superadmin",
            tenant_id=None,  # Superadmin has no tenant
            is_active=True,
        )

        db.add(superadmin)
        await db.commit()
        await db.refresh(superadmin)

        print(f"\n=== Superadmin Created Successfully ===")
        print(f"ID: {superadmin.id}")
        print(f"Email: {superadmin.email}")
        print(f"Full Name: {superadmin.full_name}")
        print(f"Role: {superadmin.role}")
        print(f"Tenant ID: {superadmin.tenant_id} (NULL - global access)")
        print(f"\nYou can now log in at /api/v1/auth/login")


if __name__ == "__main__":
    asyncio.run(create_superadmin())
