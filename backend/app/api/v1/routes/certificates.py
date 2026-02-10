"""
Calibration certificate management API endpoints.

Provides CRUD operations for calibration certificates with:
- Create certificate (tenant_admin, superadmin)
- List certificates with pagination and tenant filter
- Get certificate by ID
- Update certificate
- Soft delete (set is_active=False)
- Upload PDF file
"""

import io
import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_filter, require_role
from app.models.calibration_certificate import CalibrationCertificate
from app.models.user import User
from app.schemas.certificate import (
    CertificateCreate,
    CertificateUpdate,
    CertificateResponse,
    CertificateListResponse,
)
from app.services.storage import get_storage_service, StorageError

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.post("/", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
async def create_certificate(
    data: CertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))] = None,
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Create a new calibration certificate.

    Requires tenant_admin or superadmin role.
    Superadmin must specify tenant_id via query parameter.
    """
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar tenant_id na query (?tenant_id=...)",
        )

    # Check for duplicate certificate_number within the tenant
    existing = await db.execute(
        select(CalibrationCertificate).where(
            and_(
                CalibrationCertificate.tenant_id == tenant_id,
                CalibrationCertificate.certificate_number == data.certificate_number,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Certificado com numero '{data.certificate_number}' ja existe neste tenant",
        )

    certificate = CalibrationCertificate(
        tenant_id=tenant_id,
        equipment_name=data.equipment_name,
        certificate_number=data.certificate_number,
        manufacturer=data.manufacturer,
        model=data.model,
        serial_number=data.serial_number,
        laboratory=data.laboratory,
        calibration_date=data.calibration_date,
        expiry_date=data.expiry_date,
        status=data.status,
    )
    db.add(certificate)
    await db.commit()
    await db.refresh(certificate)

    return CertificateResponse.model_validate(certificate)


@router.get("/", response_model=CertificateListResponse)
async def list_certificates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    search: str | None = Query(None, description="Search by equipment name or certificate number"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    active_only: bool = Query(True, description="Show only active certificates"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List calibration certificates for the current tenant.

    Supports search, status filter, and pagination.
    """
    conditions = []
    if tenant_id is not None:
        conditions.append(CalibrationCertificate.tenant_id == tenant_id)

    if active_only:
        conditions.append(CalibrationCertificate.is_active == True)

    if status_filter:
        conditions.append(CalibrationCertificate.status == status_filter)

    if search:
        search_term = f"%{search}%"
        conditions.append(
            CalibrationCertificate.equipment_name.ilike(search_term)
            | CalibrationCertificate.certificate_number.ilike(search_term)
        )

    # Count total
    count_query = select(func.count(CalibrationCertificate.id)).where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get certificates
    query = (
        select(CalibrationCertificate)
        .where(and_(*conditions))
        .order_by(CalibrationCertificate.expiry_date.asc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    certificates = result.scalars().all()

    return CertificateListResponse(
        certificates=[CertificateResponse.model_validate(c) for c in certificates],
        total=total,
    )


@router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(
    certificate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """Get a calibration certificate by ID."""
    conditions = [CalibrationCertificate.id == certificate_id]
    if tenant_id is not None:
        conditions.append(CalibrationCertificate.tenant_id == tenant_id)

    result = await db.execute(
        select(CalibrationCertificate).where(and_(*conditions))
    )
    certificate = result.scalar_one_or_none()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    return CertificateResponse.model_validate(certificate)


@router.patch("/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: UUID,
    data: CertificateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))] = None,
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Update a calibration certificate.

    Requires tenant_admin or superadmin role.
    """
    conditions = [CalibrationCertificate.id == certificate_id]
    if tenant_id is not None:
        conditions.append(CalibrationCertificate.tenant_id == tenant_id)

    result = await db.execute(
        select(CalibrationCertificate).where(and_(*conditions))
    )
    certificate = result.scalar_one_or_none()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    # Check for duplicate certificate_number if being changed
    update_data = data.model_dump(exclude_unset=True)
    if "certificate_number" in update_data and update_data["certificate_number"] != certificate.certificate_number:
        existing = await db.execute(
            select(CalibrationCertificate).where(
                and_(
                    CalibrationCertificate.tenant_id == certificate.tenant_id,
                    CalibrationCertificate.certificate_number == update_data["certificate_number"],
                    CalibrationCertificate.id != certificate_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Certificado com numero '{update_data['certificate_number']}' ja existe neste tenant",
            )

    for field, value in update_data.items():
        setattr(certificate, field, value)

    await db.commit()
    await db.refresh(certificate)

    return CertificateResponse.model_validate(certificate)


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(
    certificate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))] = None,
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Soft delete a calibration certificate (set is_active=False).

    Requires tenant_admin or superadmin role.
    """
    conditions = [CalibrationCertificate.id == certificate_id]
    if tenant_id is not None:
        conditions.append(CalibrationCertificate.tenant_id == tenant_id)

    result = await db.execute(
        select(CalibrationCertificate).where(and_(*conditions))
    )
    certificate = result.scalar_one_or_none()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    certificate.is_active = False
    await db.commit()

    return None


@router.post("/{certificate_id}/upload", response_model=CertificateResponse)
async def upload_certificate_file(
    certificate_id: UUID,
    file: UploadFile = File(..., description="Certificate PDF file"),
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))] = None,
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Upload a PDF file for a calibration certificate.

    Requires tenant_admin or superadmin role.
    Stores the file and updates the certificate's file_key.
    """
    # Validate file type
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser PDF",
        )

    conditions = [CalibrationCertificate.id == certificate_id]
    if tenant_id is not None:
        conditions.append(CalibrationCertificate.tenant_id == tenant_id)

    result = await db.execute(
        select(CalibrationCertificate).where(and_(*conditions))
    )
    certificate = result.scalar_one_or_none()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    # Delete old file if exists
    storage = get_storage_service()
    if certificate.file_key:
        try:
            storage.delete_object(certificate.file_key)
        except Exception:
            pass

    # Upload new file
    try:
        file_key = f"{certificate.tenant_id}/certificates/{certificate_id}/{file.filename or 'certificate.pdf'}"
        content = await file.read()
        file_obj = io.BytesIO(content)

        url, stored_key = storage.upload_photo(
            file=file_obj,
            tenant_id=str(certificate.tenant_id),
            report_id="certificates",
            response_id=str(certificate_id),
            original_filename=file.filename or "certificate.pdf",
            content_type="application/pdf",
        )
        certificate.file_key = stored_key
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    await db.commit()
    await db.refresh(certificate)

    return CertificateResponse.model_validate(certificate)
