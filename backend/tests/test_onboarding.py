"""
Tests for the Onboarding guided setup system.

Covers:
- GET onboarding status (new tenant, all pending)
- Complete a step (branding -> completed)
- Skip a step (certificate -> skipped)
- Clone demo template (creates template with sections/fields)
- All steps completed -> is_completed=True
- Invalid step key -> 400
- Technician RBAC -> 403
- Provisioning auto-creates onboarding record
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.main import app
from app.models.template import Template
from app.models.template_section import TemplateSection
from app.models.tenant_onboarding import TenantOnboarding
from app.models.tenant_plan import TenantPlan
from app.models.user import User
from tests.conftest import _make_user, _override_get_db, _override_get_current_user
from tests.factories import create_tenant


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _client_for(session: AsyncSession, user: User) -> AsyncClient:
    """Return an AsyncClient whose auth is bound to *user*."""
    app.dependency_overrides[get_db] = _override_get_db(session)
    app.dependency_overrides[get_current_user] = _override_get_current_user(user)
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def _create_plan(db: AsyncSession, name: str = "Test Plan") -> TenantPlan:
    """Create a TenantPlan directly in the database."""
    plan = TenantPlan(
        name=name,
        description="Plan for testing",
        limits_json={"max_users": 10, "max_storage_gb": 5.0, "max_reports_month": 100},
        features_json={
            "gps_required": True,
            "certificate_required": False,
            "export_excel": True,
            "watermark": True,
            "custom_pdf": False,
        },
        is_active=True,
        price_display="R$ 99/mes",
    )
    db.add(plan)
    await db.flush()
    return plan


# ---------------------------------------------------------------------------
# GET /onboarding/status - New tenant (all pending)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_status_new_tenant(admin_client: AsyncClient, test_tenant):
    """GET /onboarding/status for a new tenant returns all steps pending."""
    resp = await admin_client.get("/api/v1/onboarding/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_completed"] is False
    assert data["current_step"] == 0
    assert len(data["steps"]) == 4
    for step in data["steps"]:
        assert step["status"] == "pending"
    assert data["steps"][0]["key"] == "branding"
    assert data["steps"][3]["key"] == "first_report"


# ---------------------------------------------------------------------------
# Complete branding step
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_branding_step(admin_client: AsyncClient, test_tenant):
    """PUT /onboarding/step/branding with action=complete marks it completed."""
    resp = await admin_client.put(
        "/api/v1/onboarding/step/branding",
        json={"action": "complete"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["step_key"] == "branding"
    assert data["new_status"] == "completed"
    assert data["current_step"] == 1  # Moved to next pending step
    assert data["is_completed"] is False


# ---------------------------------------------------------------------------
# Skip certificate step
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skip_certificate_step(admin_client: AsyncClient, test_tenant):
    """PUT /onboarding/step/certificate with action=skip marks it skipped."""
    resp = await admin_client.put(
        "/api/v1/onboarding/step/certificate",
        json={"action": "skip"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["step_key"] == "certificate"
    assert data["new_status"] == "skipped"


# ---------------------------------------------------------------------------
# Clone demo template
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clone_demo_template(admin_client: AsyncClient, test_tenant, db_session: AsyncSession):
    """POST /onboarding/clone-demo-template creates template with sections and fields."""
    resp = await admin_client.post("/api/v1/onboarding/clone-demo-template")
    assert resp.status_code == 201
    data = resp.json()
    assert "template_id" in data
    assert data["template_name"] == "CPQ11 - Comissionamento de Quadros Eletricos"
    assert data["template_code"] == "CPQ11-DEMO"

    # Verify sections were created
    result = await db_session.execute(
        select(TemplateSection).where(TemplateSection.template_id == data["template_id"])
    )
    sections = result.scalars().all()
    assert len(sections) == 3

    # Verify idempotency - calling again returns same template
    resp2 = await admin_client.post("/api/v1/onboarding/clone-demo-template")
    assert resp2.status_code == 201
    assert resp2.json()["template_id"] == data["template_id"]


# ---------------------------------------------------------------------------
# All steps completed -> is_completed=True
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_steps_completed(admin_client: AsyncClient, test_tenant):
    """Completing all steps sets is_completed=True."""
    steps = ["branding", "template", "certificate", "first_report"]
    for step in steps:
        resp = await admin_client.put(
            f"/api/v1/onboarding/step/{step}",
            json={"action": "complete"},
        )
        assert resp.status_code == 200

    # Check final step response
    data = resp.json()
    assert data["is_completed"] is True

    # Verify via status endpoint
    status_resp = await admin_client.get("/api/v1/onboarding/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["is_completed"] is True
    assert status_resp.json()["completed_at"] is not None


# ---------------------------------------------------------------------------
# Invalid step key -> 400
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_step_key(admin_client: AsyncClient, test_tenant):
    """PUT /onboarding/step/invalid returns 400."""
    resp = await admin_client.put(
        "/api/v1/onboarding/step/invalid_step",
        json={"action": "complete"},
    )
    assert resp.status_code == 400
    assert "Invalid step key" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Technician RBAC -> 403
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_technician_blocked(tech_client: AsyncClient, test_tenant):
    """Technician gets 403 on onboarding endpoints."""
    resp = await tech_client.get("/api/v1/onboarding/status")
    assert resp.status_code == 403

    resp = await tech_client.put(
        "/api/v1/onboarding/step/branding",
        json={"action": "complete"},
    )
    assert resp.status_code == 403

    resp = await tech_client.post("/api/v1/onboarding/clone-demo-template")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Provisioning auto-creates onboarding record
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_provisioning_creates_onboarding(client: AsyncClient, db_session: AsyncSession):
    """POST /superadmin/tenants auto-creates onboarding record for new tenant."""
    plan = await _create_plan(db_session, name=f"OnbPlan-{uuid.uuid4().hex[:6]}")
    slug = f"onb-tenant-{uuid.uuid4().hex[:6]}"

    resp = await client.post(
        "/api/v1/superadmin/tenants",
        json={
            "name": "Onboarding Test Corp",
            "slug": slug,
            "plan_id": str(plan.id),
            "admin_email": f"admin-{uuid.uuid4().hex[:6]}@onb.com",
            "admin_password": "SecurePass123!",
            "admin_full_name": "Onboarding Admin",
            "trial_days": 14,
        },
    )
    assert resp.status_code == 201
    tenant_id = resp.json()["id"]

    # Verify onboarding record was created
    result = await db_session.execute(
        select(TenantOnboarding).where(TenantOnboarding.tenant_id == tenant_id)
    )
    onboarding = result.scalar_one_or_none()
    assert onboarding is not None
    assert onboarding.is_completed is False
    assert onboarding.current_step == 0
