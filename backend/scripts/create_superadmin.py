#!/usr/bin/env python3
"""
Create the initial superadmin user for SmartHand.

Usage:
    # With environment variables:
    SUPERADMIN_EMAIL=admin@smarthand.com.br \
    SUPERADMIN_PASSWORD=SuaSenhaSegura123! \
    SUPERADMIN_NAME="Alexandre Conti" \
    python scripts/create_superadmin.py

    # Or run interactively (will prompt for values)
    python scripts/create_superadmin.py
"""

import asyncio
import os
import sys
from getpass import getpass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session as AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def create_superadmin():
    """Create the initial superadmin user."""
    print("\n=== SmartHand - Criar Superadmin ===\n")

    # Get values from environment or prompt
    email = os.environ.get("SUPERADMIN_EMAIL")
    password = os.environ.get("SUPERADMIN_PASSWORD")
    full_name = os.environ.get("SUPERADMIN_NAME")

    if not email:
        email = input("Email: ").strip()
    if not full_name:
        full_name = input("Nome completo: ").strip()
    if not password:
        password = getpass("Senha: ")

    # Validate inputs
    if not email or "@" not in email:
        print("Erro: Email invalido")
        return False

    if not full_name or len(full_name) < 2:
        print("Erro: Nome deve ter pelo menos 2 caracteres")
        return False

    if not password or len(password) < 8:
        print("Erro: Senha deve ter pelo menos 8 caracteres")
        return False

    # Connect to database
    async with AsyncSessionLocal() as db:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"Erro: Email '{email}' ja existe")
            return False

        # Check if superadmin already exists
        result = await db.execute(select(User).where(User.role == "superadmin"))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Aviso: Ja existe um superadmin: {existing.email}")
            if os.environ.get("SUPERADMIN_EMAIL"):
                # Non-interactive mode, skip
                print("Abortando em modo nao-interativo")
                return False
            confirm = input("Criar outro? (sim/nao): ").strip().lower()
            if confirm != "sim":
                return False

        # Create superadmin
        superadmin = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role="superadmin",
            tenant_id=None,
            is_active=True,
        )

        db.add(superadmin)
        await db.commit()
        await db.refresh(superadmin)

        print(f"\n=== Superadmin Criado ===")
        print(f"ID: {superadmin.id}")
        print(f"Email: {superadmin.email}")
        print(f"Nome: {superadmin.full_name}")
        print(f"Role: superadmin (acesso global)")
        print(f"\nAcesse: /api/v1/auth/login")
        return True


if __name__ == "__main__":
    import selectors
    selector = selectors.SelectSelector()
    loop = asyncio.SelectorEventLoop(selector)
    try:
        success = loop.run_until_complete(create_superadmin())
    finally:
        loop.close()
    sys.exit(0 if success else 1)
