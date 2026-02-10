"""
Test configuration and fixtures for SmartHand backend tests.
"""
import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.tenant import Tenant


# Use test database URL
TEST_DATABASE_URL = settings.database_url


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session-scoped async fixtures."""
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create async engine and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with rollback."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Company",
        slug="test-company",
        is_active=True,
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def second_tenant(db_session: AsyncSession) -> Tenant:
    """Create a second test tenant for isolation tests."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Other Company",
        slug="other-company",
        is_active=True,
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


def _make_user(tenant_id=None, role="technician", **kwargs):
    """Helper to create user objects."""
    from app.core.security import hash_password
    defaults = {
        "id": uuid.uuid4(),
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "full_name": "Test User",
        "password_hash": hash_password("Test1234!"),
        "role": role,
        "tenant_id": tenant_id,
        "is_active": True,
    }
    defaults.update(kwargs)
    return User(**defaults)


@pytest_asyncio.fixture
async def superadmin_user(db_session: AsyncSession) -> User:
    """Create a superadmin user (no tenant_id)."""
    user = _make_user(tenant_id=None, role="superadmin", full_name="Super Admin")
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def tenant_admin_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a tenant admin user."""
    user = _make_user(tenant_id=test_tenant.id, role="tenant_admin", full_name="Tenant Admin")
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def technician_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a technician user."""
    user = _make_user(tenant_id=test_tenant.id, role="technician", full_name="Tech User")
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a viewer user."""
    user = _make_user(tenant_id=test_tenant.id, role="viewer", full_name="Viewer User")
    db_session.add(user)
    await db_session.flush()
    return user


def _override_get_db(session: AsyncSession):
    """Create a get_db override that returns the test session."""
    async def _get_db():
        yield session
    return _get_db


def _override_get_current_user(user: User):
    """Create a get_current_user override that returns a specific user."""
    async def _get_current_user():
        return user
    return _get_current_user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, superadmin_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test client (default: superadmin)."""
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    app.dependency_overrides[get_current_user] = _override_get_current_user(superadmin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(db_session: AsyncSession, tenant_admin_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test client as tenant_admin."""
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    app.dependency_overrides[get_current_user] = _override_get_current_user(tenant_admin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def tech_client(db_session: AsyncSession, technician_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test client as technician."""
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    app.dependency_overrides[get_current_user] = _override_get_current_user(technician_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
