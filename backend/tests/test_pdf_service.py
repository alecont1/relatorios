"""
Unit tests for PDFService and the PDF merger utility.

Uses mock Report / Tenant objects to exercise PDF generation without a
running database or HTTP server.
"""
import uuid
from datetime import date, datetime
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.pdf_service import PDFService
from app.services.pdf_merger import merge_report_with_certificates


# ---------------------------------------------------------------------------
# Helpers -- lightweight stand-ins for ORM models
# ---------------------------------------------------------------------------


def _mock_tenant(**overrides) -> SimpleNamespace:
    """Create a minimal tenant-like object."""
    defaults = dict(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        logo_primary_key=None,
        logo_secondary_key=None,
        brand_color_primary="#2563eb",
        contact_phone="+55 11 9999-0000",
        contact_email="contato@test.com",
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _mock_report(
    tenant_id: uuid.UUID | None = None,
    template_snapshot: dict | None = None,
    **overrides,
) -> SimpleNamespace:
    """Create a minimal report-like object."""
    tid = tenant_id or uuid.uuid4()
    snapshot = template_snapshot or {
        "name": "Template de Teste",
        "code": "TST-001",
        "version": 1,
        "info_fields": [],
        "sections": [
            {
                "name": "Secao 1",
                "order": 1,
                "fields": [
                    {
                        "label": "Item A",
                        "field_type": "dropdown",
                        "options": "Sim,Nao",
                        "order": 1,
                    },
                ],
            }
        ],
        "signature_fields": [],
    }

    # Simulate info_values and checklist_responses
    info_values = overrides.pop("info_values", [])
    checklist_responses = overrides.pop("checklist_responses", [
        SimpleNamespace(
            section_name="Secao 1",
            section_order=1,
            field_label="Item A",
            field_order=1,
            field_type="dropdown",
            response_value="Sim",
            comment="OK",
            photos=[],
        ),
    ])
    signatures = overrides.pop("signatures", [])

    defaults = dict(
        id=uuid.uuid4(),
        tenant_id=tid,
        template_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Relatorio de Teste",
        status="completed",
        location=None,
        template_snapshot=snapshot,
        started_at=datetime(2025, 6, 1, 10, 0),
        completed_at=datetime(2025, 6, 1, 12, 0),
        created_at=datetime(2025, 6, 1, 10, 0),
        updated_at=datetime(2025, 6, 1, 12, 0),
        info_values=info_values,
        checklist_responses=checklist_responses,
        signatures=signatures,
        certificates=[],
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _mock_certificate(**overrides) -> SimpleNamespace:
    """Create a minimal certificate-like object."""
    defaults = dict(
        id=uuid.uuid4(),
        equipment_name="Multimetro Fluke 87V",
        certificate_number="CERT-001",
        laboratory="LabCal Ltda",
        calibration_date=date(2025, 1, 15),
        expiry_date=date(2026, 1, 15),
        status="valid",
        file_key=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _minimal_pdf() -> bytes:
    """Generate a minimal but valid single-page PDF using fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Test PDF content")
    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# PDFService tests
# ---------------------------------------------------------------------------


svc = PDFService()


def test_generate_report_pdf_basic():
    """generate_report_pdf returns non-empty bytes starting with %PDF."""
    tenant = _mock_tenant()
    report = _mock_report(tenant_id=tenant.id)

    pdf_bytes = svc.generate_report_pdf(report, tenant)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 100
    assert pdf_bytes[:5] == b"%PDF-"


def test_generate_report_pdf_with_certificates():
    """Including certificates adds a certificates section to the PDF."""
    tenant = _mock_tenant()
    report = _mock_report(tenant_id=tenant.id)
    certs = [_mock_certificate(), _mock_certificate(certificate_number="CERT-002")]

    pdf_bytes = svc.generate_report_pdf(report, tenant, certificates=certs)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:5] == b"%PDF-"
    # The PDF should be larger when certificates are included
    basic_bytes = svc.generate_report_pdf(report, tenant)
    assert len(pdf_bytes) >= len(basic_bytes)


# ---------------------------------------------------------------------------
# PDF Merger tests
# ---------------------------------------------------------------------------


def test_merge_with_certificates():
    """merge_report_with_certificates produces a valid merged PDF."""
    report_pdf = _minimal_pdf()
    cert_pdf = _minimal_pdf()

    merged = merge_report_with_certificates(report_pdf, [cert_pdf])
    assert isinstance(merged, bytes)
    assert merged[:5] == b"%PDF-"
    # Merged should be at least as large as the report alone
    assert len(merged) >= len(report_pdf)


def test_merge_empty_certificates():
    """When cert_files is empty, the original report PDF is returned."""
    report_pdf = _minimal_pdf()
    result = merge_report_with_certificates(report_pdf, [])
    assert result == report_pdf


def test_merge_invalid_cert_skipped():
    """Invalid certificate bytes are silently skipped in the merge."""
    report_pdf = _minimal_pdf()
    invalid_bytes = b"this is not a valid pdf"
    valid_cert = _minimal_pdf()

    # Should not raise; invalid cert is skipped, valid one is merged
    merged = merge_report_with_certificates(report_pdf, [invalid_bytes, valid_cert])
    assert isinstance(merged, bytes)
    assert merged[:5] == b"%PDF-"
