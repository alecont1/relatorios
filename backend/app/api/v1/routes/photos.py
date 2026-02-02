"""
Photo management API endpoints.

Handles photo uploads, deletion, and listing for report checklist responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.report import Report
from app.models.report_checklist_response import ReportChecklistResponse
from app.services.storage import get_storage_service, StorageError
from app.schemas.photo import (
    PhotoMetadata,
    GPSCoordinates,
    PhotoUploadResponse,
    PhotoDeleteResponse,
    PhotoListResponse,
)

router = APIRouter(prefix="/reports/{report_id}/photos", tags=["photos"])


async def get_report_with_access(
    report_id: UUID,
    db: AsyncSession,
    user: User,
) -> Report:
    """Get report and verify user has access."""
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .where(Report.tenant_id == user.tenant_id)
        .options(selectinload(Report.checklist_responses))
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return report


@router.post("", response_model=PhotoUploadResponse)
async def upload_photo(
    report_id: UUID,
    response_id: str = Form(..., description="Checklist response ID"),
    file: UploadFile = File(..., description="Photo file"),
    captured_at: Optional[str] = Form(None, description="Capture timestamp ISO format"),
    latitude: Optional[float] = Form(None, ge=-90, le=90),
    longitude: Optional[float] = Form(None, ge=-180, le=180),
    gps_accuracy: Optional[float] = Form(None, ge=0),
    address: Optional[str] = Form(None, description="Reverse geocoded address"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a photo to a checklist response.

    The photo will be stored in cloud storage (R2) or local filesystem.
    Metadata including GPS coordinates and timestamp are stored with the photo.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    # Check report status - can only add photos to draft or in_progress
    if report.status not in ("draft", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add photos to completed or archived reports"
        )

    # Find the checklist response
    response = next(
        (r for r in report.checklist_responses if str(r.id) == response_id),
        None
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist response not found"
        )

    # Check photo count limit from template snapshot
    current_photos = response.photos or []
    max_photos = _get_max_photos_for_field(report, response)
    if max_photos and len(current_photos) >= max_photos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_photos} photos allowed for this field"
        )

    # Upload to storage
    storage = get_storage_service()
    try:
        url, storage_path = storage.upload_photo(
            file=file.file,
            tenant_id=str(current_user.tenant_id),
            report_id=str(report_id),
            response_id=response_id,
            original_filename=file.filename or "photo.jpg",
            content_type=file.content_type or "image/jpeg",
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    # Build GPS coordinates if provided
    gps = None
    if latitude is not None and longitude is not None:
        gps = GPSCoordinates(
            latitude=latitude,
            longitude=longitude,
            accuracy=gps_accuracy,
        )

    # Parse captured_at
    capture_time = datetime.utcnow()
    if captured_at:
        try:
            capture_time = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Create photo metadata
    photo = PhotoMetadata(
        id=str(uuid.uuid4()),
        url=url,
        original_filename=file.filename,
        size_bytes=file.size,
        captured_at=capture_time,
        gps=gps,
        address=address,
        watermarked=False,  # Will be set to True when frontend sends watermarked image
    )

    # Update response photos array
    photos_list = list(current_photos)
    photos_list.append(photo.model_dump(mode="json"))
    response.photos = photos_list

    await db.commit()

    return PhotoUploadResponse(photo=photo)


@router.delete("/{photo_id}", response_model=PhotoDeleteResponse)
async def delete_photo(
    report_id: UUID,
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a photo from a checklist response.

    Removes the photo from storage and updates the response metadata.
    """
    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    # Check report status
    if report.status not in ("draft", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete photos from completed or archived reports"
        )

    # Find the photo across all responses
    photo_found = False
    storage_path = None

    for response in report.checklist_responses:
        if not response.photos:
            continue

        photos = list(response.photos)
        for i, p in enumerate(photos):
            if p.get("id") == photo_id:
                photo_found = True
                # Extract storage path from URL for deletion
                url = p.get("url", "")
                if url.startswith("/uploads/"):
                    storage_path = url[9:]  # Remove /uploads/ prefix

                # Remove from array
                photos.pop(i)
                response.photos = photos
                break

        if photo_found:
            break

    if not photo_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete from storage
    if storage_path:
        storage = get_storage_service()
        storage.delete_object(storage_path)

    await db.commit()

    return PhotoDeleteResponse()


@router.get("", response_model=list[PhotoListResponse])
async def list_photos(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all photos for a report, grouped by checklist response.

    Returns photos organized by the checklist field they belong to.
    """
    # Get report and verify access
    report = await get_report_with_access(report_id, db, current_user)

    results = []
    for response in report.checklist_responses:
        photos = response.photos or []
        max_photos = _get_max_photos_for_field(report, response)
        required = _is_photo_required_for_field(report, response)

        if photos or required:  # Include fields with photos or required photos
            results.append(
                PhotoListResponse(
                    response_id=str(response.id),
                    field_label=response.field_label,
                    photos=[PhotoMetadata(**p) for p in photos],
                    max_photos=max_photos,
                    required=required,
                )
            )

    return results


def _get_max_photos_for_field(report: Report, response: ReportChecklistResponse) -> Optional[int]:
    """Get max photo count from template snapshot for this field."""
    snapshot = report.template_snapshot
    if not snapshot:
        return None

    for section in snapshot.get("sections", []):
        for field in section.get("fields", []):
            if field.get("id") == str(response.field_id) or field.get("label") == response.field_label:
                photo_config = field.get("photo_config", {})
                return photo_config.get("max_count")

    return None


def _is_photo_required_for_field(report: Report, response: ReportChecklistResponse) -> bool:
    """Check if photo is required from template snapshot for this field."""
    snapshot = report.template_snapshot
    if not snapshot:
        return False

    for section in snapshot.get("sections", []):
        for field in section.get("fields", []):
            if field.get("id") == str(response.field_id) or field.get("label") == response.field_label:
                photo_config = field.get("photo_config", {})
                return photo_config.get("required", False) or (photo_config.get("min_count", 0) > 0)

    return False
