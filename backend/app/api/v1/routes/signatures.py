"""
Signature management API endpoints.

Handles signature uploads, deletion, and listing for reports.
"""
from datetime import datetime
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.report import Report
from app.models.report_signature import ReportSignature
from app.services.storage import get_storage_service, StorageError
from app.schemas.signature import (
    SignatureResponse,
    SignatureListResponse,
)

router = APIRouter(prefix="/reports/{report_id}/signatures", tags=["signatures"])


async def get_report_with_access(
    report_id: UUID,
    db: AsyncSession,
    user: User,
) -> Report:
    """Get report and verify user has access."""
    query = select(Report).where(Report.id == report_id).options(selectinload(Report.signatures))

    # Superadmin (tenant_id=NULL) can access all reports
    # Regular users can only access reports from their tenant
    if user.tenant_id is not None:
        query = query.where(Report.tenant_id == user.tenant_id)

    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return report


def _get_signature_url(storage, file_key: str) -> str:
    """Get URL for signature file."""
    # For local storage, return the file path
    if hasattr(storage, 'get_download_url'):
        return storage.get_download_url(file_key)
    # Default to uploads path
    return f"/uploads/{file_key}"


@router.post("", response_model=SignatureResponse)
async def upload_signature(
    report_id: UUID,
    role_name: str = Form(..., max_length=100, description="Role name (e.g., Técnico, Supervisor)"),
    file: UploadFile = File(..., description="Signature image (PNG)"),
    signer_name: str | None = Form(None, max_length=255, description="Name of the signer"),
    signature_field_id: UUID | None = Form(None, description="Template signature field ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a signature for a report.

    The signature will be stored in cloud storage (R2) or local filesystem.
    Each role can only have one signature per report.
    """
    # Validate file type (should be PNG from canvas)
    if not file.content_type or file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature must be a PNG or JPEG image"
        )

    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    # Check report status - can only add signatures to draft or in_progress
    if report.status not in ("draft", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add signatures to completed or archived reports"
        )

    # Check if signature for this role already exists
    existing = next(
        (s for s in report.signatures if s.role_name == role_name),
        None
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature for role '{role_name}' already exists. Delete it first to replace."
        )

    # Upload to storage - use report's tenant_id for proper isolation
    storage = get_storage_service()
    try:
        file_key = f"{report.tenant_id}/signatures/{report_id}/{uuid.uuid4()}.png"
        content = await file.read()

        if hasattr(storage, 'upload_bytes'):
            storage.upload_bytes(content, file_key, "image/png")
        else:
            # Fallback: use upload_photo method structure
            import io
            file.file = io.BytesIO(content)
            url, file_key = storage.upload_photo(
                file=file.file,
                tenant_id=str(report.tenant_id),
                report_id=str(report_id),
                response_id="signatures",
                original_filename=f"{role_name}.png",
                content_type="image/png",
            )
    except (StorageError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    # Create signature record - use report's tenant_id for proper isolation
    signed_at = datetime.utcnow()
    signature = ReportSignature(
        id=uuid.uuid4(),
        tenant_id=report.tenant_id,
        report_id=report_id,
        role_name=role_name,
        signer_name=signer_name,
        file_key=file_key,
        signed_at=signed_at,
        signature_field_id=signature_field_id,
    )

    db.add(signature)
    await db.commit()
    await db.refresh(signature)

    # Get URL for response
    url = _get_signature_url(storage, file_key)

    return SignatureResponse(
        id=signature.id,
        role_name=signature.role_name,
        signer_name=signature.signer_name,
        url=url,
        signed_at=signature.signed_at,
        signature_field_id=signature.signature_field_id,
        created_at=signature.created_at,
    )


@router.delete("/{signature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signature(
    report_id: UUID,
    signature_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a signature from a report.

    Removes the signature from storage and database.
    """
    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    # Check report status
    if report.status not in ("draft", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete signatures from completed or archived reports"
        )

    # Find the signature
    signature = next(
        (s for s in report.signatures if s.id == signature_id),
        None
    )
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found"
        )

    # Delete from storage
    storage = get_storage_service()
    try:
        storage.delete_object(signature.file_key)
    except Exception:
        pass  # Continue even if storage deletion fails

    # Delete from database
    await db.delete(signature)
    await db.commit()

    return None


@router.get("", response_model=SignatureListResponse)
async def list_signatures(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all signatures for a report.

    Returns signatures with their URLs and metadata.
    """
    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    storage = get_storage_service()
    signatures = []

    for sig in report.signatures:
        url = _get_signature_url(storage, sig.file_key)
        signatures.append(
            SignatureResponse(
                id=sig.id,
                role_name=sig.role_name,
                signer_name=sig.signer_name,
                url=url,
                signed_at=sig.signed_at,
                signature_field_id=sig.signature_field_id,
                created_at=sig.created_at,
            )
        )

    return SignatureListResponse(
        signatures=signatures,
        total=len(signatures),
    )
