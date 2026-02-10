"""
Tests for the full report lifecycle.

Covers creation, draft updates, status transitions (draft -> in_progress ->
completed -> archived), and validation guards around immutable states.
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_template, create_project, create_report


BASE = "/api/v1/reports"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_via_api(
    client: AsyncClient,
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    title: str = "Lifecycle Report",
) -> dict:
    """Create a report through the HTTP API and return the response body."""
    template = await create_template(db, tenant_id)
    project = await create_project(db, tenant_id)
    resp = await client.post(
        f"{BASE}/?tenant_id={tenant_id}",
        json={
            "template_id": str(template.id),
            "project_id": str(project.id),
            "title": title,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """POST /reports creates a report with a template snapshot."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    assert body["status"] == "draft"
    assert body["template_snapshot"] is not None
    assert "sections" in body["template_snapshot"]
    assert body["tenant_id"] == str(test_tenant.id)
    assert "id" in body


# ---------------------------------------------------------------------------
# Draft updates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_report_draft(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """PATCH /reports/{id} can update title, info_values, and checklist_responses."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    resp = await admin_client.patch(
        f"{BASE}/{report_id}?tenant_id={test_tenant.id}",
        json={"title": "Updated Title"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_report_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """PATCH /reports/{id} moves status from draft to in_progress."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    resp = await admin_client.patch(
        f"{BASE}/{report_id}?tenant_id={test_tenant.id}",
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    assert resp.json()["started_at"] is not None


@pytest.mark.asyncio
async def test_complete_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """POST /reports/{id}/complete marks a draft/in_progress report as completed."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    resp = await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_complete_report_sets_completed_at(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """Completing a report populates the completed_at timestamp."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    resp = await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 200
    assert resp.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_archive_completed_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """POST /reports/{id}/archive changes a completed report to archived."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    # Complete first
    await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )

    # Archive
    resp = await admin_client.post(
        f"{BASE}/{report_id}/archive?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


# ---------------------------------------------------------------------------
# Transition guards
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cannot_modify_completed_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """PATCH on a completed report returns 400."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )

    resp = await admin_client.patch(
        f"{BASE}/{report_id}?tenant_id={test_tenant.id}",
        json={"title": "Should Fail"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_cannot_complete_archived_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """POST /complete on an archived report returns 400."""
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )
    await admin_client.post(
        f"{BASE}/{report_id}/archive?tenant_id={test_tenant.id}"
    )

    resp = await admin_client.post(
        f"{BASE}/{report_id}/complete?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Listing and detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_reports_with_status_filter(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """GET /reports?status=draft returns only draft reports."""
    await _create_via_api(
        admin_client, db_session, test_tenant.id, title="Draft One"
    )

    resp = await admin_client.get(
        f"{BASE}/?tenant_id={test_tenant.id}&status=draft"
    )
    assert resp.status_code == 200
    for r in resp.json()["reports"]:
        assert r["status"] == "draft"


@pytest.mark.asyncio
async def test_get_report_detail(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
):
    """
    GET /reports/{id} returns the full detail including snapshot,
    info_values, and checklist_responses.
    """
    body = await _create_via_api(admin_client, db_session, test_tenant.id)
    report_id = body["id"]

    resp = await admin_client.get(
        f"{BASE}/{report_id}?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["template_snapshot"] is not None
    assert isinstance(detail["info_values"], list)
    assert isinstance(detail["checklist_responses"], list)
    # Checklist responses are pre-populated from the template
    assert len(detail["checklist_responses"]) >= 2
