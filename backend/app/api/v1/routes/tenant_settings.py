"""
Tenant settings API endpoints.

Provides endpoints for tenant administrators to manage:
- Branding configuration (logos, colors)
- Contact information
- Logo uploads via R2 presigned URLs
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role, get_tenant_filter
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantBrandingUpdate, TenantResponse
from app.services.storage import get_storage_service
from pydantic import BaseModel, Field


router = APIRouter(prefix="/tenant-settings", tags=["tenant-settings"])


# Schemas for logo upload endpoints
class LogoUploadRequest(BaseModel):
    """Request schema for generating logo upload URL."""
    filename: str = Field(..., description="Original filename with extension")
    file_type: str = Field(..., description="MIME type (image/png, image/jpeg, image/svg+xml)")


class LogoUploadResponse(BaseModel):
    """Response schema with presigned upload URL."""
    upload_url: str = Field(..., description="Presigned URL for uploading logo")
    object_key: str = Field(..., description="R2 object key to use after upload")


class LogoConfirmRequest(BaseModel):
    """Request schema for confirming logo upload."""
    object_key: str = Field(..., description="R2 object key from upload response")
    logo_type: str = Field(..., description="Logo type: 'primary' or 'secondary'")


@router.get("/branding", response_model=TenantResponse)
async def get_tenant_branding(
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("tenant_admin", "superadmin"))
):
    """
    Get current tenant's branding configuration.

    Returns logo keys, brand colors, and contact information.
    Requires admin or superadmin role.
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado"
        )

    return tenant


@router.patch("/branding", response_model=TenantResponse)
async def update_tenant_branding(
    branding_data: TenantBrandingUpdate,
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("tenant_admin", "superadmin"))
):
    """
    Update tenant branding configuration.

    Allows updating:
    - Brand colors (primary, secondary, accent)
    - Contact information (address, phone, email, website)
    - Logo keys (via separate upload endpoints)

    Requires admin or superadmin role.
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado"
        )

    # Update fields from branding_data (only non-None values)
    update_data = branding_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    return tenant


@router.post("/logo/upload-url", response_model=LogoUploadResponse)
async def generate_logo_upload_url(
    request: LogoUploadRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    current_user: User = Depends(require_role("tenant_admin", "superadmin"))
):
    """
    Generate presigned URL for uploading tenant logo.

    Supports:
    - PNG (image/png)
    - JPEG (image/jpeg)
    - SVG (image/svg+xml)

    Returns presigned URL valid for 1 hour.
    Requires admin or superadmin role.
    """
    # Validate file type
    allowed_types = {"image/png", "image/jpeg", "image/svg+xml"}
    if request.file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo nao suportado. Use: {', '.join(allowed_types)}"
        )

    # Generate presigned URL
    storage = get_storage_service()
    upload_url, object_key = storage.generate_upload_url(
        tenant_id=str(tenant_id),
        filename=request.filename,
        content_type=request.file_type,
        expires_in=3600  # 1 hour
    )

    return LogoUploadResponse(
        upload_url=upload_url,
        object_key=object_key
    )


@router.post("/logo/confirm", response_model=TenantResponse)
async def confirm_logo_upload(
    request: LogoConfirmRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("tenant_admin", "superadmin"))
):
    """
    Confirm logo upload and save object key to tenant.

    After successful upload to presigned URL, call this endpoint
    to update tenant's logo_primary_key or logo_secondary_key.

    Validates that object_key belongs to current tenant.
    Requires admin or superadmin role.
    """
    # Validate logo type
    if request.logo_type not in {"primary", "secondary"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de logo invalido. Use 'primary' ou 'secondary'"
        )

    # Validate object key belongs to this tenant
    expected_prefix = f"{tenant_id}/"
    if not request.object_key.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chave de objeto nao pertence a este tenant"
        )

    # Get tenant
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado"
        )

    # Update appropriate logo field
    if request.logo_type == "primary":
        tenant.logo_primary_key = request.object_key
    else:
        tenant.logo_secondary_key = request.object_key

    await db.commit()
    await db.refresh(tenant)

    return tenant
