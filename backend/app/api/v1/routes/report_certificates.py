"""
Report-certificate association API endpoints.

Manages the link between reports and calibration certificates:
- List certificates linked to a report
- Link certificates to a report
- Unlink certificates from a report
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_filter
from app.models.calibration_certificate import CalibrationCertificate
from app.models.report import Report
from app.models.report_certificate import ReportCertificate
from app.models.user import User
from app.schemas.certificate import (
    CertificateResponse,
    CertificateListResponse,
    ReportCertificateLink,
)

router = APIRouter(prefix="/reports/{report_id}/certificates", tags=["report-certificates"])


async def _get_report_with_tenant_check(
    report_id: UUID,
    db: AsyncSession,
    tenant_id: UUID | None,
) -> Report:
    """Get report with tenant filtering."""
    conditions = [Report.id == report_id]
    if tenant_id is not None:
        conditions.append(Report.tenant_id == tenant_id)

    result = await db.execute(
        select(Report).where(and_(*conditions))
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    return report


@router.get("/", response_model=CertificateListResponse)
async def list_report_certificates(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """List all calibration certificates linked to a report."""
    report = await _get_report_with_tenant_check(report_id, db, tenant_id)

    # Query certificates linked to this report
    query = (
        select(CalibrationCertificate)
        .join(
            ReportCertificate,
            ReportCertificate.certificate_id == CalibrationCertificate.id,
        )
        .where(ReportCertificate.report_id == report.id)
        .order_by(CalibrationCertificate.equipment_name.asc())
    )
    result = await db.execute(query)
    certificates = result.scalars().all()

    return CertificateListResponse(
        certificates=[CertificateResponse.model_validate(c) for c in certificates],
        total=len(certificates),
    )


@router.post("/link", response_model=CertificateListResponse)
async def link_certificates(
    report_id: UUID,
    data: ReportCertificateLink,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Link calibration certificates to a report.

    Certificates must belong to the same tenant as the report.
    Duplicate links are silently ignored.
    """
    report = await _get_report_with_tenant_check(report_id, db, tenant_id)

    if not data.certificate_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista de certificate_ids nao pode ser vazia",
        )

    # Verify all certificates exist and belong to the same tenant
    cert_result = await db.execute(
        select(CalibrationCertificate).where(
            and_(
                CalibrationCertificate.id.in_(data.certificate_ids),
                CalibrationCertificate.tenant_id == report.tenant_id,
                CalibrationCertificate.is_active == True,
            )
        )
    )
    valid_certs = cert_result.scalars().all()
    valid_cert_ids = {c.id for c in valid_certs}

    invalid_ids = set(data.certificate_ids) - valid_cert_ids
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificados nao encontrados ou inativos: {[str(i) for i in invalid_ids]}",
        )

    # Get existing links to avoid duplicates
    existing_result = await db.execute(
        select(ReportCertificate.certificate_id).where(
            and_(
                ReportCertificate.report_id == report.id,
                ReportCertificate.certificate_id.in_(data.certificate_ids),
            )
        )
    )
    existing_cert_ids = {row[0] for row in existing_result.all()}

    # Create new links
    for cert_id in data.certificate_ids:
        if cert_id not in existing_cert_ids:
            link = ReportCertificate(
                report_id=report.id,
                certificate_id=cert_id,
            )
            db.add(link)

    await db.commit()

    # Return updated list
    query = (
        select(CalibrationCertificate)
        .join(
            ReportCertificate,
            ReportCertificate.certificate_id == CalibrationCertificate.id,
        )
        .where(ReportCertificate.report_id == report.id)
        .order_by(CalibrationCertificate.equipment_name.asc())
    )
    result = await db.execute(query)
    certificates = result.scalars().all()

    return CertificateListResponse(
        certificates=[CertificateResponse.model_validate(c) for c in certificates],
        total=len(certificates),
    )


@router.post("/unlink", response_model=CertificateListResponse)
async def unlink_certificates(
    report_id: UUID,
    data: ReportCertificateLink,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Unlink calibration certificates from a report.

    Certificates not currently linked are silently ignored.
    """
    report = await _get_report_with_tenant_check(report_id, db, tenant_id)

    if not data.certificate_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista de certificate_ids nao pode ser vazia",
        )

    # Find existing links to delete
    existing_result = await db.execute(
        select(ReportCertificate).where(
            and_(
                ReportCertificate.report_id == report.id,
                ReportCertificate.certificate_id.in_(data.certificate_ids),
            )
        )
    )
    links_to_delete = existing_result.scalars().all()

    for link in links_to_delete:
        await db.delete(link)

    await db.commit()

    # Return updated list
    query = (
        select(CalibrationCertificate)
        .join(
            ReportCertificate,
            ReportCertificate.certificate_id == CalibrationCertificate.id,
        )
        .where(ReportCertificate.report_id == report.id)
        .order_by(CalibrationCertificate.equipment_name.asc())
    )
    result = await db.execute(query)
    certificates = result.scalars().all()

    return CertificateListResponse(
        certificates=[CertificateResponse.model_validate(c) for c in certificates],
        total=len(certificates),
    )
