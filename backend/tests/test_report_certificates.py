"""
Tests for report-certificate linking API endpoints.

Covers linking, unlinking, cross-tenant rejection, and edge cases.
"""
import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calibration_certificate import CalibrationCertificate
from app.models.report_certificate import ReportCertificate
from tests.factories import create_template, create_project, create_report


BASE_REPORTS = "/api/v1/reports"


async def _setup_report(
    db: AsyncSession, tenant_id: uuid.UUID, user
) -> uuid.UUID:
    """Create a template, project, and report; return the report id."""
    template = await create_template(db, tenant_id)
    project = await create_project(db, tenant_id)
    report = await create_report(db, tenant_id, template, project, user)
    return report.id


async def _create_cert(
    db: AsyncSession, tenant_id: uuid.UUID, number: str = "LINK-001", **kw
) -> CalibrationCertificate:
    """Insert a certificate directly into the database."""
    defaults = dict(
        tenant_id=tenant_id,
        equipment_name="Test Equipment",
        certificate_number=number,
        calibration_date=date(2025, 1, 1),
        expiry_date=date(2026, 1, 1),
        status="valid",
        is_active=True,
    )
    defaults.update(kw)
    cert = CalibrationCertificate(**defaults)
    db.add(cert)
    await db.flush()
    return cert


# ---------------------------------------------------------------------------
# Link / list / unlink happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_link_certificates_to_report(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """POST /reports/{id}/certificates/link attaches certificates."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(db_session, test_tenant.id, "LNK-001")

    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] >= 1
    ids = [c["id"] for c in body["certificates"]]
    assert str(cert.id) in ids


@pytest.mark.asyncio
async def test_list_report_certificates(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """GET /reports/{id}/certificates returns linked certificates."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(db_session, test_tenant.id, "LST-001")

    # Link first
    await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )

    resp = await admin_client.get(
        f"{BASE_REPORTS}/{report_id}/certificates/?tenant_id={test_tenant.id}"
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_unlink_certificates(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """POST /reports/{id}/certificates/unlink removes the association."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(db_session, test_tenant.id, "UNL-001")

    await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )

    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/unlink?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_link_nonexistent_certificate(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """Linking a certificate ID that does not exist returns 404."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)

    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(uuid.uuid4())]},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_link_duplicate_ignored(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """Linking the same certificate twice does not raise an error."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(db_session, test_tenant.id, "DUP-LINK-001")

    await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )

    # Second link with same ID should succeed (silently ignored)
    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 1  # still only one link


@pytest.mark.asyncio
async def test_cross_tenant_link_rejected(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    second_tenant,
    tenant_admin_user,
):
    """Cannot link a certificate that belongs to a different tenant."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    other_cert = await _create_cert(
        db_session, second_tenant.id, "CROSS-001"
    )

    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(other_cert.id)]},
    )
    # The route validates tenant match and returns 404 for mismatched certs
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unlink_nonexistent_silently(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """Unlinking a certificate that is not linked does not error."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(db_session, test_tenant.id, "NOSUCH-001")

    # Unlink without having linked -- route silently ignores
    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/unlink?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_link_inactive_certificate_rejected(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant,
    tenant_admin_user,
):
    """Linking an inactive (soft-deleted) certificate returns 404."""
    report_id = await _setup_report(db_session, test_tenant.id, tenant_admin_user)
    cert = await _create_cert(
        db_session, test_tenant.id, "INACT-001", is_active=False
    )

    resp = await admin_client.post(
        f"{BASE_REPORTS}/{report_id}/certificates/link?tenant_id={test_tenant.id}",
        json={"certificate_ids": [str(cert.id)]},
    )
    assert resp.status_code == 404
