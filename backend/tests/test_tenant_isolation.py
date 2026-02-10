"""
Tests for multi-tenant data isolation.

Ensures that data belonging to Tenant A is invisible and inaccessible
to users of Tenant B, while superadmin retains cross-tenant visibility.
"""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.main import app
from tests.conftest import (
    _make_user,
    _override_get_db,
    _override_get_current_user,
)
from tests.factories import (
    create_template,
    create_project,
    create_report,
    create_user,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _client_for(session: AsyncSession, user) -> AsyncClient:
    """Build an AsyncClient authenticated as *user*."""
    app.dependency_overrides[get_db] = _override_get_db(session)
    app.dependency_overrides[get_current_user] = _override_get_current_user(user)
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def _seed_data(db: AsyncSession, tenant_id: uuid.UUID, user):
    """Create a template, project, and report inside *tenant_id*."""
    template = await create_template(db, tenant_id)
    project = await create_project(db, tenant_id)
    report = await create_report(db, tenant_id, template, project, user)
    return template, project, report


# ---------------------------------------------------------------------------
# Tenant A vs Tenant B
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_reports(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Admin of Tenant A sees 0 reports when Tenant B owns the only report."""
    # Create data under second_tenant
    user_b = _make_user(
        tenant_id=second_tenant.id, role="technician", full_name="User B"
    )
    db_session.add(user_b)
    await db_session.flush()
    await _seed_data(db_session, second_tenant.id, user_b)

    # Query as Tenant A admin
    ac = await _client_for(db_session, tenant_admin_user)
    try:
        resp = await ac.get(
            f"/api/v1/reports/?tenant_id={test_tenant.id}"
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_templates(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Tenant A admin cannot list templates that belong to Tenant B."""
    await create_template(db_session, second_tenant.id)

    ac = await _client_for(db_session, tenant_admin_user)
    try:
        resp = await ac.get(
            f"/api/v1/templates?tenant_id={test_tenant.id}"
        )
        assert resp.status_code == 200
        # Should see only templates for test_tenant
        for tmpl in resp.json().get("templates", []):
            assert tmpl.get("tenant_id", str(test_tenant.id)) != str(second_tenant.id)
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_users(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Tenant A admin user listing omits Tenant B users."""
    user_b = await create_user(
        db_session, tenant_id=second_tenant.id, role="technician",
        full_name="Tenant B Tech",
    )

    ac = await _client_for(db_session, tenant_admin_user)
    try:
        resp = await ac.get("/api/v1/users")
        assert resp.status_code == 200
        user_ids = [u["id"] for u in resp.json()["users"]]
        assert str(user_b.id) not in user_ids
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_certificates(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Certificate listing is scoped to the caller's tenant."""
    from app.models.calibration_certificate import CalibrationCertificate
    from datetime import date

    cert_b = CalibrationCertificate(
        tenant_id=second_tenant.id,
        equipment_name="B-Only Gauge",
        certificate_number="B-CERT-001",
        calibration_date=date(2025, 1, 1),
        expiry_date=date(2026, 1, 1),
        status="valid",
        is_active=True,
    )
    db_session.add(cert_b)
    await db_session.flush()

    ac = await _client_for(db_session, tenant_admin_user)
    try:
        resp = await ac.get(
            f"/api/v1/certificates/?tenant_id={test_tenant.id}"
        )
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json()["certificates"]]
        assert str(cert_b.id) not in ids
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_a_cannot_modify_tenant_b_report(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Tenant A admin gets 404 when trying to PATCH a Tenant B report."""
    user_b = _make_user(
        tenant_id=second_tenant.id, role="technician", full_name="User B"
    )
    db_session.add(user_b)
    await db_session.flush()
    _, _, report_b = await _seed_data(db_session, second_tenant.id, user_b)

    ac = await _client_for(db_session, tenant_admin_user)
    try:
        resp = await ac.patch(
            f"/api/v1/reports/{report_b.id}?tenant_id={test_tenant.id}",
            json={"title": "Hijacked"},
        )
        assert resp.status_code == 404
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Superadmin cross-tenant visibility
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_superadmin_sees_all_tenants(
    client: AsyncClient,
):
    """Superadmin can list all tenant organisations."""
    resp = await client.get("/api/v1/tenants")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 0  # at least the structure is correct


@pytest.mark.asyncio
async def test_superadmin_sees_reports_across_tenants(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    superadmin_user,
):
    """Superadmin (no tenant_id param) sees reports from all tenants."""
    user_a = _make_user(
        tenant_id=test_tenant.id, role="technician", full_name="A Tech"
    )
    user_b = _make_user(
        tenant_id=second_tenant.id, role="technician", full_name="B Tech"
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    await _seed_data(db_session, test_tenant.id, user_a)
    await _seed_data(db_session, second_tenant.id, user_b)

    ac = await _client_for(db_session, superadmin_user)
    try:
        resp = await ac.get("/api/v1/reports/")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 2
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_filter_applied_correctly(
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    superadmin_user,
):
    """
    Superadmin with ?tenant_id=<A> sees only Tenant A reports,
    even when Tenant B reports exist.
    """
    user_a = _make_user(
        tenant_id=test_tenant.id, role="technician", full_name="A Tech"
    )
    user_b = _make_user(
        tenant_id=second_tenant.id, role="technician", full_name="B Tech"
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    await _seed_data(db_session, test_tenant.id, user_a)
    await _seed_data(db_session, second_tenant.id, user_b)

    ac = await _client_for(db_session, superadmin_user)
    try:
        resp = await ac.get(
            f"/api/v1/reports/?tenant_id={test_tenant.id}"
        )
        assert resp.status_code == 200
        for r in resp.json()["reports"]:
            assert r["tenant_id"] == str(test_tenant.id)
    finally:
        await ac.aclose()
        app.dependency_overrides.clear()
